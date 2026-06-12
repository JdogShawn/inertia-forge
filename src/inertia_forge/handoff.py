"""Session handoff — a structured end-of-session brief for whoever resumes.

Richer than `pack`: it captures the active task, the dependency-ready and
blocked sets, the parallel waves, recent commits, the continuity ledger, and any
consistency drift — so a fresh session (or a teammate) resumes with full
situational awareness. `handoff` prints it; `--write` saves .forge/handoff.md.
ASCII-clean so it's safe on any console. Deterministic.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def build() -> str:
    """Assemble the handoff document as markdown text. Pure read of the store."""
    from inertia_forge import state as st, tasks as tk, taskgraph as tg
    from inertia_forge.consistency import issues
    from inertia_forge.gitcheck import _git

    plan = tk.get_plan()
    lines = ["# Session Handoff", "",
             f"**Plan:** {plan['type'] + ' - ' + plan['title'] if plan else '(none)'}",
             f"**Active task:** {tk.active_task_id() or '(none)'}", ""]
    ready = [x["id"] for x in tg.ready_tasks()]
    lines += ["## Ready to start", *([f"- {r}" for r in ready] or ["- (none)"])]
    blocked = tg.blocked_tasks()
    if blocked:
        lines += ["", "## Blocked"] + [f"- {tid} <- {', '.join(by)}"
                                       for tid, by in sorted(blocked.items())]
    waves = tg.parallel_waves()
    if waves:
        lines += ["", "## Parallel waves"] + [f"{i}. {', '.join(w)}"
                                              for i, w in enumerate(waves, 1)]
    data = st.load()
    lines += ["", "## Continuity",
              f"- last: {data['last'] or '(none)'}",
              f"- next: {data['next'] or '(none)'}"]
    commits = _git(Path("."), "log", "-5", "--format=- %s").strip()
    if commits:
        lines += ["", "## Recent commits", commits]
    drift = issues()
    if drift:
        lines += ["", "## Consistency drift"] + [f"- {d}" for d in drift]
    return "\n".join(lines) + "\n"


def run_handoff(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge handoff")
    p.add_argument("--write", action="store_true", help="save to .forge/handoff.md")
    args = p.parse_args(argv)
    doc = build()
    if args.write:
        out = Path(".forge") / "handoff.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(doc, encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(doc)
    return 0
