"""`inertia-forge learn` — a deterministic knowledge ledger (commonplace book).

Capture insights to `.forge/knowledge.jsonl`, then list/search them. No model,
no synthesis — just durable, greppable, tagged notes that survive sessions.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

KNOW = Path(".forge") / "knowledge.jsonl"


def add(text: str, tags: list[str]) -> None:
    KNOW.parent.mkdir(parents=True, exist_ok=True)
    entry = {"text": text, "tags": tags,
             "ts": datetime.now(timezone.utc).isoformat()}
    with open(KNOW, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def all_entries() -> list[dict]:
    if not KNOW.exists():
        return []
    out: list[dict] = []
    for line in KNOW.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def search(term: str) -> list[dict]:
    low = term.lower()
    return [e for e in all_entries()
            if low in e.get("text", "").lower()
            or any(low in tag.lower() for tag in e.get("tags", []))]


def _show(entries: list[dict]) -> None:
    if not entries:
        print("(none)")
        return
    for e in entries:
        tags = f"  [{', '.join(e['tags'])}]" if e.get("tags") else ""
        print(f"- {e.get('text', '')}{tags}")


def run_learn(argv: list[str]) -> int:
    if not argv:
        print("usage: inertia-forge learn [add <text> [--tag T]... | list | search <term>]")
        return 1
    # Shorthand: `learn "free text" [--tag T]` == `learn add ...` — inject the
    # subcommand so argparse (and --tag) work, instead of choking on the text.
    if argv[0] not in ("add", "list", "search"):
        argv = ["add"] + argv

    p = argparse.ArgumentParser(prog="inertia-forge learn")
    sub = p.add_subparsers(dest="sub", required=True)
    a = sub.add_parser("add", help="capture an insight")
    a.add_argument("text", nargs="+")
    a.add_argument("--tag", action="append", default=[], dest="tags")
    sub.add_parser("list", help="list all insights")
    s = sub.add_parser("search", help="search insights")
    s.add_argument("term")
    args = p.parse_args(argv)
    if args.sub == "list":
        _show(all_entries())
        return 0
    if args.sub == "search":
        _show(search(args.term))
        return 0
    add(" ".join(args.text), args.tags)
    print("captured.")
    return 0
