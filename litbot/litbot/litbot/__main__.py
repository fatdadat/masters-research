"""litbot — a local, free literature-review pipeline.

    python -m litbot discover        find papers (APIs + citation chasing)
    python -m litbot rank            score them, no LLM, instant
    python -m litbot screen          include/exclude with the local model
    python -m litbot fetch           download open-access PDFs
    python -m litbot import-pdfs DIR attach PDFs you saved by hand
    python -m litbot extract         structured extraction from PDFs
    python -m litbot zotero          push included items into Zotero
    python -m litbot report          write digest, evidence table, .bib, packet
    python -m litbot run             discover -> rank -> screen -> fetch -> extract -> report
    python -m litbot status          where everything stands
"""
from __future__ import annotations

import argparse
import sys

from . import config, stages, zotero_sync


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="litbot", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-c", "--config", default="config.yaml")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("discover", help="search the APIs and chase citations")
    p.add_argument("--no-snowball", action="store_true")
    p.add_argument("--max-per-query", type=int, default=200)

    sub.add_parser("rank", help="deterministic relevance scoring")

    p = sub.add_parser("screen", help="include/exclude with the local model")
    p.add_argument("--limit", type=int, default=60)
    p.add_argument("--rescreen", action="store_true")

    p = sub.add_parser("fetch", help="download open-access PDFs")
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--retry", action="store_true",
                   help="also re-try papers previously marked manual_needed")

    p = sub.add_parser("import-pdfs", help="attach manually downloaded PDFs")
    p.add_argument("folder")

    p = sub.add_parser("extract", help="structured extraction from PDFs")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--re-extract", action="store_true")

    p = sub.add_parser("zotero", help="sync included items to Zotero")
    p.add_argument("--limit", type=int, default=200)
    p.add_argument("--no-pdfs", action="store_true")

    p = sub.add_parser("report", help="write the output files")
    p.add_argument("--packet-size", type=int, default=25)

    p = sub.add_parser("run", help="the whole pipeline, once")
    p.add_argument("--screen-limit", type=int, default=60)
    p.add_argument("--extract-limit", type=int, default=20)

    sub.add_parser("status", help="counts by stage")

    args = ap.parse_args(argv)
    cfg = config.load(args.config)

    if args.cmd == "discover":
        stages.discover(cfg, snowball=not args.no_snowball,
                        max_per_query=args.max_per_query)
    elif args.cmd == "rank":
        stages.rank(cfg)
    elif args.cmd == "screen":
        stages.screen(cfg, limit=args.limit, rescreen=args.rescreen)
    elif args.cmd == "fetch":
        stages.fetch(cfg, limit=args.limit, retry=args.retry)
    elif args.cmd == "import-pdfs":
        stages.import_pdfs(cfg, args.folder)
    elif args.cmd == "extract":
        stages.extract(cfg, limit=args.limit, re_extract=args.re_extract)
    elif args.cmd == "zotero":
        zotero_sync.sync(cfg, limit=args.limit, attach_pdfs=not args.no_pdfs)
    elif args.cmd == "report":
        stages.report(cfg, packet_size=args.packet_size)
    elif args.cmd == "status":
        stages.status(cfg)
    elif args.cmd == "run":
        stages.discover(cfg)
        stages.rank(cfg)
        stages.screen(cfg, limit=args.screen_limit)
        stages.fetch(cfg)
        stages.extract(cfg, limit=args.extract_limit)
        stages.report(cfg)
        stages.status(cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
