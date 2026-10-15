"""Push the included corpus into Zotero.

Zotero is the right place for the paywalled half of your reading: its browser
connector saves a PDF from a publisher page you are already signed in to, one
click at a time, which is exactly what your library subscription is for. This
module handles the other direction — putting the metadata, tags and any
open-access PDFs the pipeline found into your library so everything lives in one
place and your .bib file writes itself.

Get an API key at https://www.zotero.org/settings/keys (allow library write).
Your library id is the number shown there for "Your userID for use in API calls".
"""
from __future__ import annotations

from pathlib import Path

from . import db
from .config import Config


def _client(cfg: Config):
    try:
        from pyzotero import zotero
    except ImportError:
        raise SystemExit("pip install pyzotero")
    z = cfg.zotero
    if not z.get("api_key") or not z.get("library_id"):
        raise SystemExit(
            "Set zotero.library_id and zotero.api_key in config.yaml, or the "
            "ZOTERO_LIBRARY_ID / ZOTERO_API_KEY environment variables."
        )
    return zotero.Zotero(str(z["library_id"]), z.get("library_type", "user"),
                         z["api_key"])


def _item_payload(p, collection_key: str | None, extra_tags: list[str]) -> dict:
    authors = db.decode(p["authors"], []) or []
    creators = []
    for name in authors[:40]:
        parts = name.split()
        if len(parts) >= 2:
            creators.append({"creatorType": "author", "firstName": " ".join(parts[:-1]),
                             "lastName": parts[-1]})
        elif parts:
            creators.append({"creatorType": "author", "name": parts[0]})
    tags = [{"tag": t} for t in extra_tags]
    for q in db.decode(p["screen_questions"], []) or []:
        tags.append({"tag": f"RQ{q}"})
    item = {
        "itemType": "journalArticle",
        "title": p["title"] or "",
        "creators": creators,
        "abstractNote": (p["abstract"] or "")[:6000],
        "publicationTitle": p["venue"] or "",
        "date": str(p["year"] or ""),
        "DOI": p["doi"] or "",
        "url": p["landing_url"] or (f"https://doi.org/{p['doi']}" if p["doi"] else ""),
        "tags": tags,
        "extra": f"litbot-score: {p['score']}\n{p['screen_reason'] or ''}".strip(),
    }
    if collection_key:
        item["collections"] = [collection_key]
    return item


def sync(cfg: Config, limit: int = 200, attach_pdfs: bool = True) -> None:
    zot = _client(cfg)
    collection_key = _ensure_collection(zot, cfg.zotero.get("collection", "MS-GARCH thesis"))
    extra_tags = list(cfg.zotero.get("tags", ["litbot"]))

    index = _library_index(zot)
    print(f"library already holds {len(index['by_doi'])} items with a DOI")

    with db.connect(cfg.db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM papers WHERE screen_decision = 'include' "
            "AND zotero_key IS NULL ORDER BY score DESC LIMIT ?", (limit,)
        ).fetchall()
        print(f"syncing {len(rows)} items to Zotero")
        for p in rows:
            existing = _match(index, p)
            if existing:
                key = existing
            else:
                resp = zot.create_items([_item_payload(p, collection_key, extra_tags)])
                created = (resp.get("successful") or {}).get("0")
                if not created:
                    print(f"  ! failed: {p['title'][:60]} {resp.get('failed')}")
                    continue
                key = created["key"]
            db.set_fields(conn, p["id"], zotero_key=key)
            conn.commit()

            if attach_pdfs and p["pdf_path"] and Path(p["pdf_path"]).exists():
                try:
                    zot.attachment_simple([p["pdf_path"]], key)
                except Exception as exc:  # pyzotero raises a variety of things
                    print(f"  ! attachment failed for {p['title'][:50]}: {exc}")
            print(f"  + {p['title'][:70]}")


def _ensure_collection(zot, name: str) -> str | None:
    if not name:
        return None
    for c in zot.collections():
        if c["data"]["name"] == name:
            return c["key"]
    resp = zot.create_collections([{"name": name}])
    created = (resp.get("successful") or {}).get("0")
    return created["key"] if created else None


def _library_index(zot) -> dict[str, dict]:
    """Read the whole library once and index it by DOI and by title.

    Zotero's quick search covers titles, creators and full text — it does NOT
    search the DOI field, so looking an item up by DOI through `items(q=...)`
    always comes back empty and every paper looks new. That is how a re-sync
    duplicates an entire library. Pulling the item list down once and matching
    locally is both correct and far fewer requests.
    """
    by_doi: dict[str, str] = {}
    by_title: dict[str, str] = {}
    try:
        items = zot.everything(zot.items())
    except Exception as exc:  # noqa: BLE001
        print(f"  ! could not read the library ({exc}); "
              "skipping duplicate detection")
        return {"by_doi": by_doi, "by_title": by_title}
    for it in items:
        data = it.get("data", {})
        if data.get("itemType") in {"attachment", "note", "annotation"}:
            continue
        doi = db.normalise_doi(data.get("DOI"))
        if doi and doi not in by_doi:
            by_doi[doi] = it["key"]
        title = db.normalise_title(data.get("title", ""))
        if title and title not in by_title:
            by_title[title] = it["key"]
    return {"by_doi": by_doi, "by_title": by_title}


def _match(index: dict[str, dict], p) -> str | None:
    doi = db.normalise_doi(p["doi"])
    if doi and doi in index["by_doi"]:
        return index["by_doi"][doi]
    title = p["norm_title"]
    if title and title in index["by_title"]:
        return index["by_title"][title]
    return None
    return None
