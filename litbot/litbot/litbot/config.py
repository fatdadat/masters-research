"""Configuration loading for litbot."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Config:
    raw: dict[str, Any]
    path: Path

    # --- convenience accessors -------------------------------------------------
    @property
    def workdir(self) -> Path:
        p = Path(self.raw.get("workdir", "./data")).expanduser()
        if not p.is_absolute():
            p = (self.path.parent / p).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def db_path(self) -> Path:
        return self.workdir / "corpus.sqlite"

    @property
    def pdf_dir(self) -> Path:
        p = self.workdir / "pdfs"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def out_dir(self) -> Path:
        p = self.workdir / "out"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def email(self) -> str:
        return self.raw.get("email", "")

    @property
    def queries(self) -> list[dict[str, Any]]:
        return self.raw.get("queries", [])

    @property
    def seeds(self) -> list[dict[str, Any]]:
        return self.raw.get("seeds", [])

    @property
    def scoring(self) -> dict[str, Any]:
        return self.raw.get("scoring", {})

    @property
    def ollama(self) -> dict[str, Any]:
        return self.raw.get("ollama", {})

    @property
    def zotero(self) -> dict[str, Any]:
        z = dict(self.raw.get("zotero", {}))
        # Environment variables win, so the key need not live in the file.
        if os.environ.get("ZOTERO_API_KEY"):
            z["api_key"] = os.environ["ZOTERO_API_KEY"]
        if os.environ.get("ZOTERO_LIBRARY_ID"):
            z["library_id"] = os.environ["ZOTERO_LIBRARY_ID"]
        return z

    @property
    def review_questions(self) -> dict[str, str]:
        return self.raw.get("review_questions", {})

    @property
    def proxy_prefix(self) -> str:
        """EZproxy-style prefix used ONLY to build links you click yourself."""
        return self.raw.get("library_proxy_prefix", "")


def load(path: str | Path = "config.yaml") -> Config:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise SystemExit(
            f"No config at {p}. Copy config.example.yaml to config.yaml and edit it."
        )
    with p.open() as fh:
        raw = yaml.safe_load(fh) or {}
    if not raw.get("email"):
        raise SystemExit(
            "config.yaml needs an 'email:' — OpenAlex/Crossref/Unpaywall require a "
            "contact address for their polite API pools."
        )
    return Config(raw=raw, path=p)
