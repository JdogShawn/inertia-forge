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


def _run_pack(argv: list[str]) -> int:
    from inertia_forge.handoff_pack import pack, unpack
    p = argparse.ArgumentParser(prog="inertia-forge handoff pack")
    p.add_argument("task_id")
    p.add_argument("--to", default="generic", help="target agent (claude/codex/cursor/generic)")
    p.add_argument("--from", dest="frm", default="claude", help="source agent")
    p.add_argument("--summary", default="", help="summary of work done so far")
    p.add_argument("--out", default=None, help="output .tgz path")
    a = p.parse_args(argv)
    out = pack(a.task_id, target_agent=a.to, source_agent=a.frm,
               conversation_summary=a.summary,
               output_path=Path(a.out) if a.out else None)
    print(f"packed {out}")
    return 0 if out.exists() else 1


def _run_unpack(argv: list[str]) -> int:
    from inertia_forge.handoff_pack import unpack
    p = argparse.ArgumentParser(prog="inertia-forge handoff unpack")
    p.add_argument("package")
    p.add_argument("--into", default=None, help="extract directory")
    a = p.parse_args(argv)
    meta = unpack(Path(a.package), Path(a.into) if a.into else None)
    print(f"unpacked task {meta.get('task_id', '?')} from {meta.get('source_agent', '?')}")
    return 0


def run_handoff(argv: list[str]) -> int:
    if argv and argv[0] == "pack":
        return _run_pack(argv[1:])
    if argv and argv[0] == "unpack":
        return _run_unpack(argv[1:])
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
