"""Command-line interface for memory-consolidator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .consolidator import Consolidator


def main() -> None:
    p = argparse.ArgumentParser(prog="memory-consolidator", description="Gen1 memory consolidator")
    p.add_argument("--db", default="memory/memory-consolidator/store.db", help="Path to SQLite database")
    p.add_argument("--candidates-dir", default="memory/candidates/", help="Path to candidates directory")
    sub = p.add_subparsers(dest="command", required=True)

    # promote
    sp = sub.add_parser("promote", help="Promote candidates")
    sp.add_argument("--all", action="store_true", help="Promote all unprocessed candidates")
    sp.add_argument("--candidate", help="Promote specific candidate file")

    # search
    ss = sub.add_parser("search", help="Search memories")
    ss.add_argument("query", help="Search query")
    ss.add_argument("--limit", type=int, default=10)

    # list
    sl = sub.add_parser("list", help="List memories")
    sl.add_argument("--type", dest="memory_type", help="Filter by memory type")
    sl.add_argument("--scope", help="Filter by scope")
    sl.add_argument("--status", default="active")
    sl.add_argument("--limit", type=int, default=100)

    # get
    sg = sub.add_parser("get", help="Get a specific memory")
    sg.add_argument("id", help="Memory id")

    # archive
    sa = sub.add_parser("archive", help="Archive a memory")
    sa.add_argument("id", help="Memory id")

    # rebuild
    sub.add_parser("rebuild", help="Rebuild database from candidates")

    # health
    sub.add_parser("health", help="Run health check")

    args = p.parse_args()

    c = Consolidator(args.db, args.candidates_dir)
    try:
        if args.command == "promote":
            if args.all:
                mems = c.promote_all()
                print(f"Promoted {len(mems)} candidates")
                for m in mems:
                    print(f"  {m.id} ← {m.candidate_id} ({m.title})")
            elif args.candidate:
                mem = c.promote(Path(args.candidate))
                print(f"Promoted: {mem.id} ({mem.title})")
            else:
                print("Use --all or --candidate <path>", file=sys.stderr)
                sys.exit(1)

        elif args.command == "search":
            results = c.search(args.query, args.limit)
            if not results:
                print("No results found")
            for m in results:
                print(f"\n--- {m.id} [{m.memory_type}] ---")
                print(f"  {m.title}")
                print(f"  scope: {m.scope} | source: {m.source}")
                print(f"  {m.content[:200]}")

        elif args.command == "list":
            mems = c.list(args.memory_type, args.scope, args.status, args.limit)
            for m in mems:
                print(f"{m.id}  [{m.status}] {m.memory_type}  {m.title}")

        elif args.command == "get":
            mem = c.get(args.id)
            print(json.dumps(mem.to_dict(), indent=2))

        elif args.command == "archive":
            mem = c.archive(args.id)
            print(f"Archived: {mem.id}")

        elif args.command == "rebuild":
            count = c.rebuild()
            print(f"Rebuilt: {count} memories created")

        elif args.command == "health":
            result = c.health_check()
            print(json.dumps(result, indent=2))
    finally:
        c.close()


if __name__ == "__main__":
    main()
