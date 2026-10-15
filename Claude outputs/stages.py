"""Pipeline stages: discover -> rank -> screen -> fetch -> extract -> report."""
from __future__ import annotations

import json
import math
import re
import sqlite3
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import db, sources
from .config import Config
from .llm import Ollama
from .sources import Http


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


# --------------------------------------------------------------------------- #
# 1. DISCOVER
# --------------------------------------------------------------------------- #
def discover(cfg: Config, snowball: bool = True, max_per_query: int = 200) -> None:
    """Run the configured queries and chase citations from the seed papers."""
    http = Http(cfg.email)
    with db.connect(cfg.db_path) as conn:
        seen_before = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]

        for q in cfg.queries:
            text = q["q"] if isinstance(q, dict) else str(q)
            engines = q.get("engines", ["openalex", "crossref"]) if isinstance(q, dict) else ["openalex"]
            _log(f"query: {text[:70]}...")
            if "openalex" in engines:
                yr = (q.get("from_year") if isinstance(q, dict) else None)
                filt = f"from_publication_date:{yr}-01-01" if yr else ""
                for w in sources.openalex_search(http, text, max_results=max_per_query,
                                                 extra_filter=filt):
                    _store(conn, sources.openalex_to_record, w, "openalex:search")
            if "crossref" in engines:
                for item in sources.crossref_search(http, text):
                    _store(conn, sources.crossref_to_record, item, "crossref")
            if "arxiv" in engines:
                for rec in sources.arxiv_search(http, text):
                    _store(conn, lambda r, _s: r, rec, "arxiv")
            if "s2" in engines:
                key = cfg.raw.get("semantic_scholar_api_key", "")
                for p in sources.s2_search(http, text, api_key=key):
                    _store(conn, lambda r, _s: sources.s2_to_record(r), p, "s2")

        if snowball:
            _snowball(cfg, conn, http)

        total = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    _log(f"corpus: {total} papers ({total - seen_before} new)")


def _store(conn, to_record, raw: Any, source: str) -> None:
    """Convert and save one search hit. A malformed record from any API is
    skipped with a note, never allowed to abort the run."""
    try:
        rec = to_record(raw, source)
        if not (rec.get("title") or "").strip():
            return
        rec["discovered_at"] = _now()
        db.upsert_paper(conn, rec)
    except Exception as exc:  # noqa: BLE001 - third-party data, anything goes
        _log(f"  ! skipped a {source} record ({exc.__class__.__name__}: {exc})")


def _resolve_seed(http: Http, seed: dict[str, Any]) -> dict | None:
    if seed.get("doi"):
        w = sources.openalex_by_doi(http, db.normalise_doi(seed["doi"]))
        if w:
            return w
    if seed.get("title"):
        return sources.openalex_by_title(http, seed["title"])
    return None


def _snowball(cfg: Config, conn: sqlite3.Connection, http: Http) -> None:
    """Backward (references) and forward (citations) chasing from the seeds."""
    for seed in cfg.seeds:
        w = _resolve_seed(http, seed)
        if not w:
            _log(f"  ! could not resolve seed: {seed.get('title', seed.get('doi'))}")
            continue
        rec = sources.openalex_to_record(w, "seed")
        rec["notes"] = "SEED"
        rec["discovered_at"] = _now()
        seed_id = db.upsert_paper(conn, rec)
        oid = rec.get("openalex_id")
        _log(f"  seed: {rec['title'][:60]} ({rec.get('year')})")

        if seed.get("backward", True):
            refs = w.get("referenced_works") or []
            for ref in sources.openalex_by_ids(http, refs):
                rid = db.upsert_paper(conn, {
                    **sources.openalex_to_record(ref, "backward"),
                    "discovered_at": _now(),
                })
                db.add_edge(conn, seed_id, rid)
            _log(f"    backward: {len(refs)} references")

        if seed.get("forward", True) and oid:
            n = 0
            cap = int(seed.get("forward_max", 300))
            for citing in sources.openalex_citing(http, oid, max_results=cap):
                cid = db.upsert_paper(conn, {
                    **sources.openalex_to_record(citing, "forward"),
                    "discovered_at": _now(),
                })
                db.add_edge(conn, cid, seed_id)
                n += 1
            _log(f"    forward: {n} citing works")
        conn.commit()


# --------------------------------------------------------------------------- #
# 2. RANK  (deterministic, free)
# --------------------------------------------------------------------------- #
def rank(cfg: Config) -> None:
    s = cfg.scoring
    title_kw = {k.lower(): v for k, v in (s.get("title_keywords") or {}).items()}
    abs_kw = {k.lower(): v for k, v in (s.get("abstract_keywords") or {}).items()}
    demote = {k.lower(): v for k, v in (s.get("demote_keywords") or {}).items()}
    venues = {v.lower(): w for v, w in (s.get("venue_bonus") or {}).items()}
    w_edge = float(s.get("citation_link_weight", 8.0))
    w_cites = float(s.get("cited_by_weight", 1.0))
    w_recent = float(s.get("recency_weight", 0.0))
    this_year = datetime.now().year

    with db.connect(cfg.db_path) as conn:
        linked = {r[0] for r in conn.execute("SELECT src FROM edges")} | {
            r[0] for r in conn.execute("SELECT dst FROM edges")
        }
        for p in db.all_papers(conn):
            title = (p["title"] or "").lower()
            abstract = (p["abstract"] or "").lower()
            detail: dict[str, float] = {}

            detail["title"] = sum(w for k, w in title_kw.items() if k in title)
            detail["abstract"] = sum(w for k, w in abs_kw.items() if k in abstract)
            detail["demote"] = -sum(
                w for k, w in demote.items() if k in title or k in abstract
            )
            detail["venue"] = next(
                (w for v, w in venues.items() if v in (p["venue"] or "").lower()), 0.0
            )
            detail["graph"] = w_edge if p["id"] in linked else 0.0
            detail["cited_by"] = w_cites * math.log1p(p["cited_by_count"] or 0)
            if w_recent and p["year"]:
                detail["recency"] = w_recent * max(0, 1 - (this_year - int(p["year"])) / 30)
            if (p["notes"] or "") == "SEED":
                detail["seed"] = 100.0

            score = round(sum(detail.values()), 3)
            db.set_fields(conn, p["id"], score=score,
                          score_detail={k: round(v, 3) for k, v in detail.items()})
        top = conn.execute(
            "SELECT COUNT(*) FROM papers WHERE score >= ?",
            (float(s.get("shortlist_threshold", 10)),),
        ).fetchone()[0]
    _log(f"scored corpus; {top} papers above the shortlist threshold")


# --------------------------------------------------------------------------- #
# 3. SCREEN  (local model, free)
# --------------------------------------------------------------------------- #
def screen(cfg: Config, limit: int = 60, rescreen: bool = False) -> None:
    ol = _ollama(cfg)
    ok, msg = ol.available()
    if not ok:
        raise SystemExit(f"Ollama not ready: {msg}")

    tmpl = _prompt(cfg, "screen")
    questions = "\n".join(f"  {k}: {v}" for k, v in cfg.review_questions.items())
    threshold = float(cfg.scoring.get("shortlist_threshold", 10))

    where = "score >= ?" + ("" if rescreen else " AND screen_decision IS NULL")
    with db.connect(cfg.db_path) as conn:
        rows = conn.execute(
            f"SELECT * FROM papers WHERE {where} ORDER BY score DESC LIMIT ?",
            (threshold, limit),
        ).fetchall()
        _log(f"screening {len(rows)} papers with {ol.model}")
        for i, p in enumerate(rows, 1):
            prompt = tmpl.format(
                questions=questions,
                title=p["title"],
                year=p["year"] or "n.d.",
                venue=p["venue"] or "unknown venue",
                authors=", ".join(db.decode(p["authors"], []) or [])[:200],
                abstract=(p["abstract"] or "(no abstract available)")[:4000],
            )
            out = ol.json(prompt) or {}
            decision = str(out.get("decision", "unsure")).lower()
            if decision not in {"include", "exclude", "unsure"}:
                decision = "unsure"
            db.set_fields(
                conn, p["id"],
                screen_decision=decision,
                screen_reason=str(out.get("reason", ""))[:500],
                screen_questions=[str(q) for q in (out.get("questions") or [])],
                screened_at=_now(),
            )
            conn.commit()
            if i % 10 == 0 or i == len(rows):
                _log(f"  {i}/{len(rows)}")
        counts = dict(conn.execute(
            "SELECT screen_decision, COUNT(*) FROM papers "
            "WHERE screen_decision IS NOT NULL GROUP BY screen_decision"
        ).fetchall())
    _log(f"screening totals: {counts}")


# --------------------------------------------------------------------------- #
# 4. FETCH  (open-access only, by design)
# --------------------------------------------------------------------------- #
def fetch(cfg: Config, limit: int = 40, retry: bool = False) -> None:
    """Download legally-free PDFs. Paywalled items go to a manual worklist.

    Every candidate URL tried here comes from an open-access index (Unpaywall,
    OpenAlex, arXiv) that has already established the copy is free to read. This
    never touches your university credentials: automated bulk downloading
    through an institutional proxy breaches publisher terms and gets accounts
    cut off, so genuinely paywalled papers go on a list for you to fetch by
    hand, which is entirely legitimate.
    """
    http = Http(cfg.email)
    with db.connect(cfg.db_path) as conn:
        where = ("(pdf_status IS NULL OR pdf_status = '' OR pdf_status = 'manual_needed')"
                 if retry else "(pdf_status IS NULL OR pdf_status = '')")
        rows = conn.execute(
            f"SELECT * FROM papers WHERE screen_decision = 'include' AND {where} "
            "ORDER BY score DESC LIMIT ?", (limit,),
        ).fetchall()
        _log(f"looking for open-access PDFs for {len(rows)} papers")
        got = manual = 0
        for i, p in enumerate(rows, 1):
            url = _try_candidates(http, p, cfg.pdf_dir)
            if url:
                path, source_url = url
                db.set_fields(conn, p["id"], pdf_path=str(path),
                              pdf_status="oa", oa_url=source_url)
                got += 1
            else:
                db.set_fields(conn, p["id"], pdf_status="manual_needed")
                manual += 1
            conn.commit()
            if i % 20 == 0:
                _log(f"  {i}/{len(rows)} — {got} found")
    _log(f"downloaded {got} open-access PDFs; {manual} need a manual fetch "
         f"(see out/manual_fetch.md after 'report')")


def _try_candidates(http: Http, p, pdf_dir: Path) -> tuple[Path, str] | None:
    """Work through every known open-access location for one paper.

    Direct PDF links first, then landing pages resolved to the PDF they
    advertise. Most repository copies are only reachable the second way, which
    is why trying just the first costs you most of the corpus.
    """
    candidates: list[str] = []
    if p["oa_url"]:
        candidates.append(p["oa_url"])
    if p["arxiv_id"]:
        candidates.append(f"https://arxiv.org/pdf/{p['arxiv_id']}")
    if p["doi"]:
        candidates += sources.unpaywall_candidates(http, p["doi"])
    if p["openalex_id"]:
        candidates += sources.openalex_pdf_candidates(http, p["openalex_id"])
    if p["doi"]:
        candidates += sources.s2_pdf_by_doi(http, p["doi"])
    # Last resort: the working-paper version, which carries its own DOI and so
    # is invisible to every lookup keyed on the journal DOI above.
    candidates += sources.find_free_versions(http, p["title"], p["year"])

    seen: set[str] = set()
    for url in candidates:
        if not url or url in seen:
            continue
        seen.add(url)
        path = _download_pdf(http, url, pdf_dir, p["id"])
        if path:
            return path, url
        resolved = sources.resolve_landing_page(http, url)
        if resolved and resolved not in seen:
            seen.add(resolved)
            path = _download_pdf(http, resolved, pdf_dir, p["id"])
            if path:
                return path, resolved
    return None


def _download_pdf(http: Http, url: str, pdf_dir: Path, pid: str) -> Path | None:
    r = http.get(url, allow_redirects=True)
    if r is None:
        return None
    head = r.content[:5]
    if head[:4] != b"%PDF":
        return None
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", pid)[:120]
    path = pdf_dir / f"{safe}.pdf"
    path.write_bytes(r.content)
    return path


def import_pdfs(cfg: Config, folder: str) -> None:
    """Attach PDFs fetched outside the pipeline.

    Searches the folder recursively, so you can point it straight at Zotero's
    storage directory: Zotero files each attachment under storage/<ITEM KEY>/,
    and because the pipeline records the Zotero key it assigned to every paper,
    those match exactly. Anything else falls back to matching on filename, then
    on the title printed on the PDF's first page.
    """
    src = Path(folder).expanduser()
    if not src.is_dir():
        raise SystemExit(f"{src} is not a directory")
    with db.connect(cfg.db_path) as conn:
        rows = db.all_papers(conn)
        by_norm = {p["norm_title"]: p for p in rows}
        by_zkey = {p["zotero_key"]: p for p in rows if p["zotero_key"]}
        matched = 0
        for pdf in sorted(src.rglob("*.pdf")):
            hit = by_zkey.get(pdf.parent.name)
            stem = db.normalise_title(pdf.stem.replace("_", " "))
            if hit is None:
                hit = by_norm.get(stem)
            if hit is None and len(stem) > 15:
                hit = next((p for p in rows if p["norm_title"] and
                            (p["norm_title"] in stem or stem in p["norm_title"])), None)
            if hit is None and (text := _pdf_text(pdf, max_pages=1)):
                head = db.normalise_title(text[:400])
                hit = next((p for p in rows if p["norm_title"] and
                            p["norm_title"][:60] in head), None)
            if hit is None:
                _log(f"  ? no match for {pdf.name}")
                continue
            dest = cfg.pdf_dir / f"{re.sub(r'[^A-Za-z0-9._-]', '_', hit['id'])[:120]}.pdf"
            if dest.resolve() != pdf.resolve():
                dest.write_bytes(pdf.read_bytes())
            db.set_fields(conn, hit["id"], pdf_path=str(dest), pdf_status="supplied")
            matched += 1
    _log(f"attached {matched} PDFs")


# --------------------------------------------------------------------------- #
# 5. EXTRACT  (local model, free)
# --------------------------------------------------------------------------- #
def extract(cfg: Config, limit: int = 20, re_extract: bool = False) -> None:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise SystemExit("pip install pymupdf")

    ol = _ollama(cfg)
    ok, msg = ol.available()
    if not ok:
        raise SystemExit(f"Ollama not ready: {msg}")
    tmpl = _prompt(cfg, "extract")
    questions = "\n".join(f"  {k}: {v}" for k, v in cfg.review_questions.items())

    where = "pdf_path IS NOT NULL AND screen_decision = 'include'"
    if not re_extract:
        where += " AND extraction IS NULL"
    with db.connect(cfg.db_path) as conn:
        rows = conn.execute(
            f"SELECT * FROM papers WHERE {where} ORDER BY score DESC LIMIT ?", (limit,)
        ).fetchall()
        _log(f"extracting from {len(rows)} PDFs with {ol.model}")
        for i, p in enumerate(rows, 1):
            text = _pdf_text(Path(p["pdf_path"]))
            if not text:
                db.set_fields(conn, p["id"], notes="pdf text extraction failed")
                continue
            excerpt = _excerpt(text, budget=int(cfg.ollama.get("excerpt_chars", 18000)))
            out = ol.json(tmpl.format(
                questions=questions,
                title=p["title"], year=p["year"] or "n.d.",
                authors=", ".join(db.decode(p["authors"], []) or [])[:200],
                venue=p["venue"] or "", excerpt=excerpt,
            ))
            if out is None:
                _log(f"  ! model returned unparseable JSON for {p['title'][:50]}")
                continue
            db.set_fields(conn, p["id"], extraction=out, extracted_at=_now())
            conn.commit()
            _log(f"  {i}/{len(rows)} {p['title'][:60]}")


def _pdf_text(path: Path, max_pages: int = 60) -> str:
    try:
        import fitz
    except ImportError:
        return ""
    try:
        doc = fitz.open(path)
    except Exception:
        return ""
    parts = [doc[i].get_text() for i in range(min(len(doc), max_pages))]
    doc.close()
    return "\n".join(parts)


def _excerpt(text: str, budget: int = 18000) -> str:
    """Front of the paper plus whatever looks like conclusions — small models
    do much better on a curated excerpt than on a truncated whole."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    if len(text) <= budget:
        return text
    head = text[: int(budget * 0.6)]
    tail_match = None
    for kw in ("conclusion", "concluding remarks", "summary and conclusion",
               "discussion"):
        m = list(re.finditer(kw, text, re.I))
        if m:
            tail_match = m[-1].start()
            break
    tail = text[tail_match: tail_match + int(budget * 0.4)] if tail_match else text[-int(budget * 0.4):]
    return head + "\n\n[...]\n\n" + tail


# --------------------------------------------------------------------------- #
# 6. REPORT
# --------------------------------------------------------------------------- #
def report(cfg: Config, packet_size: int = 25) -> None:
    http = Http(cfg.email)
    out = cfg.out_dir
    with db.connect(cfg.db_path) as conn:
        included = conn.execute(
            "SELECT * FROM papers WHERE screen_decision = 'include' ORDER BY score DESC"
        ).fetchall()
        unsure = conn.execute(
            "SELECT * FROM papers WHERE screen_decision = 'unsure' ORDER BY score DESC LIMIT 40"
        ).fetchall()
        manual = conn.execute(
            "SELECT * FROM papers WHERE pdf_status = 'manual_needed' ORDER BY score DESC"
        ).fetchall()
        stats = {
            "total": conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0],
            "screened": conn.execute(
                "SELECT COUNT(*) FROM papers WHERE screen_decision IS NOT NULL").fetchone()[0],
            "included": len(included),
            "with_pdf": conn.execute(
                "SELECT COUNT(*) FROM papers WHERE pdf_path IS NOT NULL").fetchone()[0],
            "extracted": conn.execute(
                "SELECT COUNT(*) FROM papers WHERE extraction IS NOT NULL").fetchone()[0],
        }

        _write(out / "digest.md", _digest(stats, included, unsure))
        _write(out / "evidence_table.md", _evidence_table(included))
        _write(out / "manual_fetch.md", _manual_list(manual, cfg.proxy_prefix))
        _write(out / "zotero_import_dois.txt", _doi_list(manual))
        _write(out / "claude_packet.md", _claude_packet(cfg, included[:packet_size]))
        _write_bibtex(http, conn, included, out / "corpus.bib")
    _log(f"wrote {out}/digest.md, evidence_table.md, claude_packet.md, "
         f"manual_fetch.md, corpus.bib")


def _write(path: Path, text: str) -> None:
    """Always UTF-8. Windows defaults to cp1252, which cannot encode the
    en-dashes and non-breaking hyphens that fill academic titles."""
    path.write_text(text, encoding="utf-8", newline="\n")


def _digest(stats: dict, included, unsure) -> str:
    lines = [
        "# Corpus digest", "",
        f"Generated {_now()}", "",
        "| stage | count |", "|---|---|",
        *[f"| {k} | {v} |" for k, v in stats.items()], "",
        "## Included papers", "",
    ]
    for p in included:
        qs = ", ".join(db.decode(p["screen_questions"], []) or [])
        lines.append(
            f"- **{p['title']}** ({p['year']}, {p['venue'] or 'n/a'}) — score "
            f"{p['score']}, Q[{qs}], pdf: {p['pdf_status'] or 'none'}\n"
            f"  - {p['screen_reason']}"
        )
    lines += ["", "## Unsure — worth your eye", ""]
    for p in unsure:
        lines.append(f"- {p['title']} ({p['year']}) — {p['screen_reason']}")
    return "\n".join(lines) + "\n"


EVIDENCE_COLUMNS = [
    ("citation", "Citation"), ("contribution_type", "Type"),
    ("model_or_result", "Model / result"),
    ("path_dependence_treatment", "Path dependence"),
    ("data_and_sample", "Data"), ("headline_finding", "Finding"),
    ("stated_limitation", "Limitation"), ("review_questions", "Q"),
    ("relation_to_core", "Relation to core"),
]


def _evidence_table(included) -> str:
    head = "| " + " | ".join(h for _, h in EVIDENCE_COLUMNS) + " |"
    sep = "|" + "|".join("---" for _ in EVIDENCE_COLUMNS) + "|"
    rows = [head, sep]
    for p in included:
        ex = db.decode(p["extraction"], {}) or {}
        if not ex:
            continue
        cells = []
        for key, _ in EVIDENCE_COLUMNS:
            val = ex.get(key, "")
            if key == "citation" and not val:
                authors = db.decode(p["authors"], []) or []
                val = f"{authors[0].split()[-1] if authors else '?'} ({p['year']})"
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val)
            cells.append(str(val).replace("|", "/").replace("\n", " ")[:400])
        rows.append("| " + " | ".join(cells) + " |")
    note = ("\n\n> Generated by a local model from the PDFs. Treat every cell as a "
            "claim to verify against the paper before it reaches your thesis.\n")
    return "# Evidence table\n\n" + "\n".join(rows) + note


def _manual_list(rows, proxy_prefix: str) -> str:
    lines = [
        "# Papers needing a manual fetch", "",
        "These have no legal open-access copy. Open each link in your browser "
        "while signed in to your university, and save the PDF — then run "
        "`python -m litbot import-pdfs <folder>`.", "",
        "The pipeline deliberately does not download these for you: automated "
        "bulk retrieval through an institutional proxy breaches publisher terms "
        "and is a common way for students to get their library access suspended.",
        "",
    ]
    for p in rows:
        doi = p["doi"] or ""
        url = f"https://doi.org/{doi}" if doi else (p["landing_url"] or "")
        if proxy_prefix and url:
            url = proxy_prefix.rstrip("/") + "/login?url=" + url
        lines.append(f"- [ ] {p['title']} ({p['year']}) — {url}")
    return "\n".join(lines) + "\n"


def _doi_list(rows) -> str:
    """DOIs of everything still missing a PDF, one per line.

    Paste into Zotero: Add Item by Identifier (the green plus with a wand).
    Zotero accepts a multi-line list, fetches metadata for each, and — when your
    browser session is signed in to the library — pulls the PDF with it. That is
    your subscription being used the way it is meant to be, by you, through a
    tool the library itself recommends.
    """
    return "\n".join(p["doi"] for p in rows if p["doi"]) + "\n"


def _claude_packet(cfg: Config, rows) -> str:
    """A compact, paste-ready brief: your review prompt plus the extractions."""
    parts = [
        "# Synthesis packet", "",
        "Paste this into Claude after the master literature-review prompt. "
        "Everything below was extracted locally from the PDFs by a small model — "
        "it is a starting point for synthesis, not verified fact.", "",
        "## Review questions", "",
        *[f"{k}. {v}" for k, v in cfg.review_questions.items()], "",
        "## Extracted papers", "",
    ]
    for p in rows:
        ex = db.decode(p["extraction"], {}) or {}
        authors = db.decode(p["authors"], []) or []
        parts.append(f"### {p['title']} ({p['year']})")
        parts.append(f"*{', '.join(authors[:4])}* — {p['venue'] or 'n/a'}"
                     + (f" — doi:{p['doi']}" if p["doi"] else ""))
        if ex:
            for key, label in EVIDENCE_COLUMNS[1:]:
                val = ex.get(key)
                if isinstance(val, list):
                    val = ", ".join(str(v) for v in val)
                if val:
                    parts.append(f"- **{label}**: {val}")
            if ex.get("key_claims"):
                parts.append("- **Claims to verify**: " +
                             "; ".join(str(c) for c in ex["key_claims"]))
        else:
            parts.append(f"- (not extracted) abstract: "
                         f"{textwrap.shorten(p['abstract'] or '', 400)}")
        parts.append("")
    return "\n".join(parts)


def _write_bibtex(http: Http, conn, rows, path: Path) -> None:
    entries = []
    for p in rows:
        if p["doi"]:
            bib = sources.crossref_bibtex(http, p["doi"])
            if bib:
                entries.append(bib.strip())
                continue
        entries.append(_fallback_bibtex(p))
    _write(path, "\n\n".join(entries) + "\n")


def _fallback_bibtex(p) -> str:
    authors = db.decode(p["authors"], []) or []
    key = re.sub(r"\W", "", (authors[0].split()[-1] if authors else "anon")) + str(p["year"] or "")
    return textwrap.dedent(f"""\
        @article{{{key},
          title = {{{p['title']}}},
          author = {{{' and '.join(authors)}}},
          year = {{{p['year'] or ''}}},
          journal = {{{p['venue'] or ''}}},
          note = {{VERIFY: assembled without a Crossref record}}
        }}""")


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _ollama(cfg: Config) -> Ollama:
    o = cfg.ollama
    return Ollama(
        host=o.get("host", "http://localhost:11434"),
        model=o.get("model", "qwen2.5:7b-instruct"),
        num_ctx=int(o.get("num_ctx", 8192)),
        temperature=float(o.get("temperature", 0.0)),
        timeout=int(o.get("timeout", 600)),
    )


def _prompt(cfg: Config, name: str) -> str:
    custom = cfg.path.parent / "prompts" / f"{name}.txt"
    if custom.exists():
        return custom.read_text(encoding="utf-8")
    builtin = Path(__file__).parent / "prompts" / f"{name}.txt"
    return builtin.read_text(encoding="utf-8")


STATUS_QUERIES = [
    ("corpus", "SELECT COUNT(*) FROM papers"),
    ("  scored", "SELECT COUNT(*) FROM papers WHERE score IS NOT NULL"),
    ("  screened", "SELECT COUNT(*) FROM papers WHERE screen_decision IS NOT NULL"),
    ("    include", "SELECT COUNT(*) FROM papers WHERE screen_decision = 'include'"),
    ("    unsure", "SELECT COUNT(*) FROM papers WHERE screen_decision = 'unsure'"),
    ("    exclude", "SELECT COUNT(*) FROM papers WHERE screen_decision = 'exclude'"),
    ("  pdfs held", "SELECT COUNT(*) FROM papers WHERE pdf_path IS NOT NULL"),
    ("  manual fetch", "SELECT COUNT(*) FROM papers WHERE pdf_status = 'manual_needed'"),
    ("  extracted", "SELECT COUNT(*) FROM papers WHERE extraction IS NOT NULL"),
    ("  in zotero", "SELECT COUNT(*) FROM papers WHERE zotero_key IS NOT NULL"),
]


def status(cfg: Config) -> None:
    with db.connect(cfg.db_path) as conn:
        for label, sql in STATUS_QUERIES:
            print(f"{label:<16} {conn.execute(sql).fetchone()[0]}")
