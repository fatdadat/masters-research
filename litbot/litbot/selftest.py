"""Offline self-test: exercises the store, dedupe, scoring and report writers
without touching the network or Ollama. Run it after setup to confirm the
install works:  python selftest.py
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import yaml

from litbot import config, db, stages

FIXTURES = [
    dict(doi="10.1093/jjfinec/nbh020",
         title="A New Approach to Markov-Switching GARCH Models",
         authors=["Markus Haas", "Stefan Mittnik", "Marc S. Paolella"], year=2004,
         venue="Journal of Financial Econometrics",
         abstract="We present a new Markov-switching GARCH model that overcomes "
                  "the path dependence problem. Dynamic properties are derived.",
         cited_by_count=800, sources=["test"]),
    # Same paper, different capitalisation and no DOI -> must merge, not duplicate.
    dict(title="A new approach to markov-switching GARCH models",
         authors=["M. Haas"], year=2004, venue="J Financial Econometrics",
         abstract="Shorter abstract that must not overwrite the longer one.",
         cited_by_count=12, sources=["test2"]),
    dict(doi="10.1016/j.csda.2013.01.026",
         title="Maximum likelihood estimation of the Markov-switching GARCH model",
         authors=["Maciej Augustyniak"], year=2014,
         venue="Computational Statistics & Data Analysis",
         abstract="An EM algorithm for quasi-maximum likelihood estimation of the "
                  "Markov switching GARCH model with path dependence.",
         cited_by_count=120, sources=["test"]),
    dict(doi="10.1234/offtopic.2021",
         title="Forecasting wind speed with a regime switching model",
         authors=["A. N. Other"], year=2021, venue="Renewable Energy",
         abstract="We apply a regime switching model to wind speed data.",
         cited_by_count=3, sources=["test"]),
]

CONFIG = {
    "email": "test@example.com",
    "workdir": "./data",
    "review_questions": {"1": "why regimes", "2": "path dependence"},
    "seeds": [],
    "queries": [],
    "scoring": {
        "shortlist_threshold": 10,
        "citation_link_weight": 8,
        "cited_by_weight": 1.0,
        "recency_weight": 1.0,
        "title_keywords": {"markov-switching": 8, "garch": 6, "regime switching": 7},
        "abstract_keywords": {"path dependence": 5, "markov switching": 3},
        "demote_keywords": {"wind speed": 8},
        "venue_bonus": {"journal of financial econometrics": 5},
    },
    "ollama": {}, "zotero": {},
}


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="litbot-selftest-"))
    try:
        cfg_path = tmp / "config.yaml"
        cfg_path.write_text(yaml.safe_dump(CONFIG))
        cfg = config.load(cfg_path)

        with db.connect(cfg.db_path) as conn:
            for rec in FIXTURES:
                db.upsert_paper(conn, dict(rec))
            rows = db.all_papers(conn)

        assert len(rows) == 3, f"dedupe failed: expected 3 papers, got {len(rows)}"
        haas = next(r for r in rows if "New Approach" in r["title"] or "new approach" in r["title"])
        assert "path dependence" in (haas["abstract"] or "").lower(), \
            "merge overwrote the longer abstract"
        assert haas["cited_by_count"] == 800, "merge lost the higher citation count"
        assert set(db.decode(haas["sources"], [])) == {"test", "test2"}, \
            "sources were not unioned"
        print("dedupe + merge      ok")

        stages.rank(cfg)
        with db.connect(cfg.db_path) as conn:
            scored = sorted(db.all_papers(conn), key=lambda r: -(r["score"] or 0))
        assert "GARCH" in scored[0]["title"] or "garch" in scored[0]["title"].lower()
        wind = next(r for r in scored if "wind" in r["title"].lower())
        assert wind["score"] < scored[0]["score"], "demotion did not work"
        detail = db.decode(scored[0]["score_detail"], {})
        assert detail.get("title", 0) > 0 and "cited_by" in detail
        print(f"scoring             ok (top={scored[0]['score']}, wind={wind['score']})")

        # Screening decisions are normally the model's; fake them to test reports.
        with db.connect(cfg.db_path) as conn:
            for r in scored[:2]:
                db.set_fields(conn, r["id"], screen_decision="include",
                              screen_reason="test", screen_questions=["1", "2"],
                              extraction={
                                  "citation": "Haas et al. (2004)",
                                  "contribution_type": "methodological",
                                  "model_or_result": "independent-switching GARCH",
                                  "path_dependence_treatment": "exact",
                                  "data_and_sample": "daily exchange rates",
                                  "headline_finding": "parallel recursions remove path dependence",
                                  "stated_limitation": "none stated in excerpt",
                                  "review_questions": ["2"],
                                  "relation_to_core": "core",
                                  "key_claims": ["stationarity condition, Section 2"],
                              })
            db.set_fields(conn, wind["id"], screen_decision="exclude",
                          screen_reason="off topic")

        # Report without network: bibtex falls back when Crossref is unreachable.
        try:
            stages.report(cfg, packet_size=5)
        except Exception as exc:  # network-free environments
            print(f"report              skipped network step ({exc.__class__.__name__})")
        out = cfg.out_dir
        for name in ("digest.md", "evidence_table.md", "claude_packet.md",
                     "manual_fetch.md"):
            assert (out / name).exists(), f"{name} not written"
        table = (out / "evidence_table.md").read_text()
        assert "independent-switching GARCH" in table, "extraction missing from table"
        packet = (out / "claude_packet.md").read_text()
        assert "Claims to verify" in packet
        print("report writers      ok")

        stages.status(cfg)
        print("\nAll self-tests passed.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
