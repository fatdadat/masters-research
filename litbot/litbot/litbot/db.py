"""SQLite store for the paper corpus.

One row per paper, keyed by a stable internal id. Everything the pipeline learns
about a paper (scores, screening decisions, extractions, file paths) lives here,
so every stage is resumable and nothing is ever paid for twice.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import unicodedata
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS papers (
    id              TEXT PRIMARY KEY,   -- doi if known, else 'title:<hash>'
    doi             TEXT,
    openalex_id     TEXT,
    arxiv_id        TEXT,
    s2_id           TEXT,
    title           TEXT NOT NULL,
    norm_title      TEXT NOT NULL,
    authors         TEXT,               -- json list
    year            INTEGER,
    venue           TEXT,
    abstract        TEXT,
    cited_by_count  INTEGER DEFAULT 0,
    oa_url          TEXT,
    landing_url     TEXT,
    sources         TEXT,               -- json list: how we found it
    discovered_at   TEXT,
    score           REAL,
    score_detail    TEXT,               -- json
    screen_decision TEXT,               -- include | exclude | unsure | null
    screen_reason   TEXT,
    screen_questions TEXT,              -- json list of review-question ids
    screened_at     TEXT,
    pdf_path        TEXT,
    pdf_status      TEXT,               -- oa | manual_needed | missing | supplied
    extraction      TEXT,               -- json
    extracted_at    TEXT,
    zotero_key      TEXT,
    notes           TEXT
);
CREATE INDEX IF NOT EXISTS idx_papers_norm_title ON papers(norm_title);
CREATE INDEX IF NOT EXISTS idx_papers_score ON papers(score DESC);
CREATE INDEX IF NOT EXISTS idx_papers_screen ON papers(screen_decision);

CREATE TABLE IF NOT EXISTS edges (
    src TEXT NOT NULL,   -- citing paper id
    dst TEXT NOT NULL,   -- cited paper id
    PRIMARY KEY (src, dst)
);

CREATE TABLE IF NOT EXISTS runs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    stage      TEXT,
    started_at TEXT,
    finished_at TEXT,
    detail     TEXT
);
"""

_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^a-z0-9 ]+")


def normalise_title(title: str) -> str:
    """Aggressive normalisation, used only for duplicate detection."""
    t = unicodedata.normalize("NFKD", title or "").lower()
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = _PUNCT.sub(" ", t)
    return _WS.sub(" ", t).strip()


def normalise_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    d = doi.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if d.startswith(prefix):
            d = d[len(prefix):]
    return d or None


def paper_id(doi: str | None, title: str) -> str:
    d = normalise_doi(doi)
    if d:
        return d
    # hashlib, not hash(): Python's string hashing is salted per process, which
    # would give the same paper a different id on every run.
    nt = normalise_title(title)
    return "title:" + hashlib.sha1(nt.encode("utf-8")).hexdigest()[:16]


@contextmanager
def connect(path: Path) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def upsert_paper(conn: sqlite3.Connection, rec: dict[str, Any]) -> str:
    """Insert or merge a paper record. Returns the paper id.

    Merge rules: never overwrite a non-empty field with an empty one; union the
    'sources' list; keep the longest abstract seen.
    """
    pid = rec.get("id") or paper_id(rec.get("doi"), rec.get("title", ""))
    rec["id"] = pid
    rec.setdefault("norm_title", normalise_title(rec.get("title", "")))
    rec["doi"] = normalise_doi(rec.get("doi"))

    existing = conn.execute("SELECT * FROM papers WHERE id = ?", (pid,)).fetchone()
    if existing is None and rec["norm_title"]:
        # Same paper under a different id (e.g. preprint without a DOI).
        existing = conn.execute(
            "SELECT * FROM papers WHERE norm_title = ?", (rec["norm_title"],)
        ).fetchone()
        if existing is not None:
            pid = existing["id"]
            rec["id"] = pid

    if existing is None:
        cols = [c for c in rec if c in _COLUMNS]
        placeholders = ", ".join("?" for _ in cols)
        conn.execute(
            f"INSERT INTO papers ({', '.join(cols)}) VALUES ({placeholders})",
            [_encode(rec[c]) for c in cols],
        )
        return pid

    merged: dict[str, Any] = {}
    for col in _COLUMNS:
        if col not in rec:
            continue
        new, old = rec[col], existing[col]
        if col == "sources":
            merged[col] = _encode(sorted(set(_decode_list(old)) | set(rec[col] or [])))
        elif col == "abstract":
            merged[col] = new if len(new or "") > len(old or "") else old
        elif col == "cited_by_count":
            merged[col] = max(int(new or 0), int(old or 0))
        elif new not in (None, "", [], {}):
            merged[col] = _encode(new)
    if merged:
        assignments = ", ".join(f"{c} = ?" for c in merged)
        conn.execute(
            f"UPDATE papers SET {assignments} WHERE id = ?",
            [*merged.values(), pid],
        )
    return pid


def add_edge(conn: sqlite3.Connection, src: str, dst: str) -> None:
    conn.execute("INSERT OR IGNORE INTO edges (src, dst) VALUES (?, ?)", (src, dst))


def get(conn: sqlite3.Connection, pid: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM papers WHERE id = ?", (pid,)).fetchone()


def find_by_doi(conn: sqlite3.Connection, doi: str) -> sqlite3.Row | None:
    d = normalise_doi(doi)
    if not d:
        return None
    return conn.execute("SELECT * FROM papers WHERE doi = ?", (d,)).fetchone()


def all_papers(conn: sqlite3.Connection, where: str = "", args: Iterable = ()) -> list[sqlite3.Row]:
    sql = "SELECT * FROM papers"
    if where:
        sql += " WHERE " + where
    return list(conn.execute(sql, tuple(args)).fetchall())


def set_fields(conn: sqlite3.Connection, pid: str, **fields: Any) -> None:
    if not fields:
        return
    assignments = ", ".join(f"{k} = ?" for k in fields)
    conn.execute(
        f"UPDATE papers SET {assignments} WHERE id = ?",
        [*(_encode(v) for v in fields.values()), pid],
    )


def _encode(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value


def _decode_list(value: Any) -> list:
    if not value:
        return []
    try:
        out = json.loads(value)
        return out if isinstance(out, list) else []
    except (TypeError, ValueError):
        return []


def decode(value: Any, default: Any = None) -> Any:
    if value in (None, ""):
        return default
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default


_COLUMNS = {
    "id", "doi", "openalex_id", "arxiv_id", "s2_id", "title", "norm_title",
    "authors", "year", "venue", "abstract", "cited_by_count", "oa_url",
    "landing_url", "sources", "discovered_at", "score", "score_detail",
    "screen_decision", "screen_reason", "screen_questions", "screened_at",
    "pdf_path", "pdf_status", "extraction", "extracted_at", "zotero_key", "notes",
}
