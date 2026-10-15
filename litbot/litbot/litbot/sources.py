"""Adapters for free bibliographic APIs.

All of these are open, documented and free. None of them require your university
credentials, and none of them are scraped: they are the APIs the publishers and
indexers provide for exactly this purpose.

  OpenAlex          metadata + citation graph (no key; be polite, send a mailto)
  Crossref          metadata + BibTeX via content negotiation (no key)
  arXiv             preprints, full text PDFs (no key)
  Semantic Scholar  metadata + TLDRs (optional key raises the rate limit)
  Unpaywall         legal open-access PDF locations for a DOI (no key, mailto)
"""
from __future__ import annotations

import re
import time
import xml.etree.ElementTree as ET
from html import unescape
from typing import Any, Iterator
from urllib.parse import quote_plus, urljoin

import requests

USER_AGENT = "litbot/1.0 (academic literature review helper)"
TIMEOUT = 30


class Http:
    """Tiny polite HTTP wrapper: shared session, per-host pacing, retries."""

    def __init__(self, email: str, min_interval: float = 0.15) -> None:
        self.email = email
        self.min_interval = min_interval
        self._last: dict[str, float] = {}
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": f"{USER_AGENT} mailto:{email}"})

    def get(self, url: str, params: dict | None = None, tries: int = 3, **kw) -> requests.Response | None:
        host = url.split("/")[2] if "//" in url else url
        for attempt in range(tries):
            wait = self.min_interval - (time.time() - self._last.get(host, 0))
            if wait > 0:
                time.sleep(wait)
            self._last[host] = time.time()
            try:
                r = self.session.get(url, params=params, timeout=TIMEOUT, **kw)
            except requests.RequestException:
                time.sleep(2 ** attempt)
                continue
            if r.status_code == 429 or 500 <= r.status_code < 600:
                time.sleep(2 ** attempt * 2)
                continue
            if r.status_code >= 400:
                return None
            return r
        return None


# --------------------------------------------------------------------------- #
# OpenAlex
# --------------------------------------------------------------------------- #
OPENALEX = "https://api.openalex.org"


def _abstract_from_inverted(index: dict[str, list[int]] | None) -> str:
    if not index:
        return ""
    positions: list[tuple[int, str]] = []
    for word, locs in index.items():
        positions.extend((loc, word) for loc in locs)
    positions.sort()
    return " ".join(word for _, word in positions)


def openalex_to_record(w: dict[str, Any], source: str) -> dict[str, Any]:
    loc = w.get("primary_location") or {}
    src = (loc.get("source") or {}) if isinstance(loc, dict) else {}
    best_oa = w.get("best_oa_location") or {}
    authors = [
        (a.get("author") or {}).get("display_name", "")
        for a in (w.get("authorships") or [])
    ]
    oid = (w.get("id") or "").rsplit("/", 1)[-1] or None
    return {
        "doi": w.get("doi"),
        "openalex_id": oid,
        "title": w.get("display_name") or w.get("title") or "",
        "authors": [a for a in authors if a],
        "year": w.get("publication_year"),
        "venue": src.get("display_name") or "",
        "abstract": _abstract_from_inverted(w.get("abstract_inverted_index")),
        "cited_by_count": w.get("cited_by_count") or 0,
        "oa_url": (best_oa.get("pdf_url") or (w.get("open_access") or {}).get("oa_url") or ""),
        "landing_url": loc.get("landing_page_url") or "",
        "sources": [source],
    }


def openalex_search(http: Http, query: str, per_page: int = 100,
                    max_results: int = 200, extra_filter: str = "") -> Iterator[dict]:
    """Full-text-ish search over titles/abstracts."""
    cursor = "*"
    fetched = 0
    while cursor and fetched < max_results:
        params = {
            "search": query,
            "per-page": min(per_page, max_results - fetched),
            "cursor": cursor,
            "mailto": http.email,
        }
        if extra_filter:
            params["filter"] = extra_filter
        r = http.get(f"{OPENALEX}/works", params=params)
        if r is None:
            return
        payload = r.json()
        results = payload.get("results", [])
        if not results:
            return
        for w in results:
            yield w
            fetched += 1
        cursor = (payload.get("meta") or {}).get("next_cursor")


def openalex_by_doi(http: Http, doi: str) -> dict | None:
    r = http.get(f"{OPENALEX}/works/https://doi.org/{doi}", params={"mailto": http.email})
    return r.json() if r is not None else None


def openalex_by_title(http: Http, title: str) -> dict | None:
    r = http.get(
        f"{OPENALEX}/works",
        params={"filter": f"title.search:{title}", "per-page": 5, "mailto": http.email},
    )
    if r is None:
        return None
    results = r.json().get("results", [])
    return results[0] if results else None


def openalex_by_ids(http: Http, ids: list[str]) -> Iterator[dict]:
    """Batch-fetch works by OpenAlex id, falling back to one-by-one."""
    for i in range(0, len(ids), 50):
        chunk = [c.rsplit("/", 1)[-1] for c in ids[i:i + 50]]
        r = http.get(
            f"{OPENALEX}/works",
            params={"filter": "openalex_id:" + "|".join(chunk),
                    "per-page": 50, "mailto": http.email},
        )
        if r is not None and r.json().get("results"):
            yield from r.json()["results"]
            continue
        for cid in chunk:  # fallback
            rr = http.get(f"{OPENALEX}/works/{cid}", params={"mailto": http.email})
            if rr is not None:
                yield rr.json()


def openalex_citing(http: Http, openalex_id: str, max_results: int = 300) -> Iterator[dict]:
    """Forward citation chasing: works that cite this one."""
    cursor = "*"
    fetched = 0
    while cursor and fetched < max_results:
        r = http.get(
            f"{OPENALEX}/works",
            params={"filter": f"cites:{openalex_id}", "per-page": 100,
                    "cursor": cursor, "mailto": http.email},
        )
        if r is None:
            return
        payload = r.json()
        for w in payload.get("results", []):
            yield w
            fetched += 1
        cursor = (payload.get("meta") or {}).get("next_cursor")
        if not payload.get("results"):
            return


# --------------------------------------------------------------------------- #
# Crossref
# --------------------------------------------------------------------------- #
CROSSREF = "https://api.crossref.org"


def crossref_search(http: Http, query: str, rows: int = 60) -> Iterator[dict]:
    r = http.get(
        f"{CROSSREF}/works",
        params={"query.bibliographic": query, "rows": rows, "mailto": http.email,
                "select": "DOI,title,author,container-title,issued,abstract,"
                          "is-referenced-by-count,URL,type"},
    )
    if r is None:
        return
    for item in (r.json().get("message") or {}).get("items", []):
        yield item


def crossref_to_record(item: dict[str, Any], source: str = "crossref") -> dict[str, Any]:
    issued = ((item.get("issued") or {}).get("date-parts") or [[None]])[0]
    authors = [
        " ".join(x for x in [a.get("given"), a.get("family")] if x)
        for a in (item.get("author") or [])
    ]
    abstract = _strip_tags(item.get("abstract") or "")
    return {
        "doi": item.get("DOI"),
        "title": (item.get("title") or [""])[0],
        "authors": authors,
        "year": issued[0] if issued else None,
        "venue": (item.get("container-title") or [""])[0],
        "abstract": abstract.strip(),
        "cited_by_count": item.get("is-referenced-by-count") or 0,
        "landing_url": item.get("URL") or "",
        "sources": [source],
    }


_TAG = re.compile(r"<[^>]+>")


def _strip_tags(text: str) -> str:
    """Crossref abstracts are JATS fragments: namespaced tags (<jats:p>) with no
    declarations, so they are not well-formed XML and must not be parsed as
    such. Strip tags textually and unescape entities."""
    if not text:
        return ""
    text = _TAG.sub(" ", text)
    text = unescape(text)
    text = re.sub(r"^\s*Abstract\b[:.]?\s*", "", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()


def crossref_bibtex(http: Http, doi: str) -> str | None:
    r = http.get(f"{CROSSREF}/works/{quote_plus(doi)}/transform/application/x-bibtex")
    return r.text if r is not None else None


# --------------------------------------------------------------------------- #
# arXiv
# --------------------------------------------------------------------------- #
ARXIV_NS = {"a": "http://www.w3.org/2005/Atom"}


def arxiv_search(http: Http, query: str, max_results: int = 50) -> Iterator[dict]:
    r = http.get(
        "http://export.arxiv.org/api/query",
        params={"search_query": f"all:{query}", "max_results": max_results,
                "sortBy": "relevance"},
    )
    if r is None:
        return
    try:
        root = ET.fromstring(r.text)
    except ET.ParseError:
        return
    for entry in root.findall("a:entry", ARXIV_NS):
        def _t(tag: str) -> str:
            el = entry.find(f"a:{tag}", ARXIV_NS)
            return (el.text or "").strip() if el is not None else ""

        pdf = ""
        for link in entry.findall("a:link", ARXIV_NS):
            if link.get("title") == "pdf":
                pdf = link.get("href", "")
        arxiv_url = _t("id")
        doi_el = entry.find("{http://arxiv.org/schemas/atom}doi")
        yield {
            "doi": (doi_el.text if doi_el is not None else None),
            "arxiv_id": arxiv_url.rsplit("/", 1)[-1],
            "title": " ".join(_t("title").split()),
            "authors": [
                (a.find("a:name", ARXIV_NS).text or "")
                for a in entry.findall("a:author", ARXIV_NS)
            ],
            "year": int(_t("published")[:4]) if _t("published")[:4].isdigit() else None,
            "venue": "arXiv preprint",
            "abstract": " ".join(_t("summary").split()),
            "oa_url": pdf,
            "landing_url": arxiv_url,
            "sources": ["arxiv"],
        }


# --------------------------------------------------------------------------- #
# Semantic Scholar (optional)
# --------------------------------------------------------------------------- #
S2 = "https://api.semanticscholar.org/graph/v1"
S2_FIELDS = ("title,abstract,year,venue,externalIds,citationCount,"
             "openAccessPdf,authors.name")


def s2_search(http: Http, query: str, limit: int = 50, api_key: str = "") -> Iterator[dict]:
    headers = {"x-api-key": api_key} if api_key else {}
    r = http.get(f"{S2}/paper/search",
                 params={"query": query, "limit": min(limit, 100), "fields": S2_FIELDS},
                 headers=headers)
    if r is None:
        return
    for p in r.json().get("data", []) or []:
        yield p


def s2_to_record(p: dict[str, Any]) -> dict[str, Any]:
    ext = p.get("externalIds") or {}
    oa = p.get("openAccessPdf") or {}
    return {
        "doi": ext.get("DOI"),
        "s2_id": p.get("paperId"),
        "arxiv_id": ext.get("ArXiv"),
        "title": p.get("title") or "",
        "authors": [a.get("name", "") for a in (p.get("authors") or [])],
        "year": p.get("year"),
        "venue": p.get("venue") or "",
        "abstract": p.get("abstract") or "",
        "cited_by_count": p.get("citationCount") or 0,
        "oa_url": oa.get("url") or "",
        "sources": ["semanticscholar"],
    }


# --------------------------------------------------------------------------- #
# Unpaywall
# --------------------------------------------------------------------------- #
def unpaywall_pdf(http: Http, doi: str) -> str | None:
    """The single best open-access PDF URL for a DOI, if one exists."""
    cands = unpaywall_candidates(http, doi)
    return cands[0] if cands else None


def unpaywall_candidates(http: Http, doi: str) -> list[str]:
    """Every open-access location Unpaywall knows for a DOI, best first.

    Returns direct PDF links ahead of landing pages. A landing page here is
    still an open-access location — Unpaywall only lists copies the publisher
    or repository has made freely available — so resolving one to its PDF is
    reading a free copy, not circumventing anything.
    """
    r = http.get(f"https://api.unpaywall.org/v2/{quote_plus(doi)}",
                 params={"email": http.email})
    if r is None:
        return []
    try:
        data = r.json()
    except ValueError:
        return []
    pdfs: list[str] = []
    pages: list[str] = []
    locs = [data.get("best_oa_location") or {}, *(data.get("oa_locations") or [])]
    for loc in locs:
        if not isinstance(loc, dict):
            continue
        if loc.get("url_for_pdf"):
            pdfs.append(loc["url_for_pdf"])
        elif loc.get("url"):
            pages.append(loc["url"])
    return _dedupe(pdfs + pages)


def openalex_pdf_candidates(http: Http, openalex_id: str) -> list[str]:
    """All open-access locations OpenAlex holds for a work, PDFs first."""
    r = http.get(f"{OPENALEX}/works/{openalex_id}", params={"mailto": http.email})
    if r is None:
        return []
    try:
        w = r.json()
    except ValueError:
        return []
    pdfs, pages = [], []
    for loc in (w.get("locations") or []):
        if not isinstance(loc, dict) or not loc.get("is_oa"):
            continue
        if loc.get("pdf_url"):
            pdfs.append(loc["pdf_url"])
        elif loc.get("landing_page_url"):
            pages.append(loc["landing_page_url"])
    return _dedupe(pdfs + pages)


_META_PDF = re.compile(
    r"""<meta[^>]+name=["']citation_pdf_url["'][^>]+content=["']([^"']+)["']""",
    re.I)
_META_PDF_REV = re.compile(
    r"""<meta[^>]+content=["']([^"']+)["'][^>]+name=["']citation_pdf_url["']""",
    re.I)
_HREF_PDF = re.compile(r"""href=["']([^"']+\.pdf(?:\?[^"']*)?)["']""", re.I)


def resolve_landing_page(http: Http, url: str) -> str | None:
    """Given an open-access landing page, find the PDF it advertises.

    Repositories publish `citation_pdf_url` in their HTML head precisely so
    that indexers and reference managers can find the file; this reads that
    tag, and falls back to the first .pdf link on the page.
    """
    r = http.get(url)
    if r is None:
        return None
    ctype = (r.headers.get("content-type") or "").lower()
    if "pdf" in ctype or r.content[:4] == b"%PDF":
        return url
    if "html" not in ctype:
        return None
    html = r.text[:400_000]
    for pattern in (_META_PDF, _META_PDF_REV):
        m = pattern.search(html)
        if m:
            return urljoin(url, unescape(m.group(1)))
    m = _HREF_PDF.search(html)
    if m:
        return urljoin(url, unescape(m.group(1)))
    return None


def _dedupe(urls: list[str]) -> list[str]:
    seen, out = set(), []
    for u in urls:
        if u and u not in seen:
            seen.add(u)
            out.append(u)
    return out
