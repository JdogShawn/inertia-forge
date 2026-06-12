"""Feedback capture — `.forge/feedback.jsonl`. Deterministic, zero LLM.

Distinct from `learn` (an agent's lessons): feedback is signal *about the work
or the process* — what to do differently, a correction, a preference. Captured,
listed, and searchable so it isn't lost between sessions.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

FEEDBACK = Path(".forge") / "feedback.jsonl"


def add(text: str, kind: str = "note") -> None:
    FEEDBACK.parent.mkdir(parents=True, exist_ok=True)
    entry = {"text": text, "kind": kind, "ts": datetime.now(timezone.utc).isoformat()}
    with open(FEEDBACK, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def all_entries() -> list[dict]:
    if not FEEDBACK.exists():
        return []
    out = []
    for line in FEEDBACK.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def run_feedback(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge feedback")
    sub = p.add_subparsers(dest="sub", required=True)
    a = sub.add_parser("add")
    a.add_argument("text", nargs="+")
    a.add_argument("--kind", default="note", help="note / correction / preference / praise")
    sub.add_parser("list")
    args = p.parse_args(argv)
    if args.sub == "add":
        add(" ".join(args.text), args.kind)
        print("feedback captured")
        return 0
    entries = all_entries()
    if not entries:
        print("(no feedback)")
        return 0
    for e in entries:
        print(f"  [{e.get('kind', 'note')}] {e.get('text', '')}")
    return 0
