"""`inertia-forge standup` — deterministic daily summary.

Aggregates real signals (no LLM): recent git commits, task progress, the
continuity ledger, and token totals — into one standup view.
"""
from __future__ import annotations

import argparse
import subprocess

from inertia_forge import metrics as m, state as st, tasks as tk


def _commits(since: str) -> list[str]:
    try:
        r = subprocess.run(["git", "log", f"--since={since}", "--oneline"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return []
    return [ln for ln in r.stdout.splitlines() if ln.strip()] if r.returncode == 0 else []


def _print_tasks() -> None:
    tasks = tk.list_tasks()
    if not tasks:
        print("  (no tasks)")
        return
    counts = {"done": 0, "in_progress": 0, "pending": 0}
    for x in tasks:
        counts[x["status"]] = counts.get(x["status"], 0) + 1
    print(f"  {counts['done']} done · {counts['in_progress']} in progress · {counts['pending']} pending")
    for x in tasks:
        if x["status"] == "in_progress":
            print(f"  -> {x['id']}: {x['title']}")


def run_standup(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="inertia-forge standup")
    parser.add_argument("--since", default="1 day ago", help="git --since window")
    args = parser.parse_args(argv)

    print(f"## Commits (since {args.since})")
    commits = _commits(args.since)
    print("\n".join(f"  {c}" for c in commits) if commits else "  (none)")

    print("\n## Tasks")
    _print_tasks()

    data = st.load()
    print("\n## Continuity")
    print(f"  last: {data['last'] or '(none)'}")
    print(f"  next: {data['next'] or '(none)'}")

    by_model = m.totals()
    if by_model:
        print("\n## Tokens")
        for model, d in sorted(by_model.items()):
            print(f"  {model}: in={d['in']} out={d['out']}")
    return 0
