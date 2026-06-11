"""Per-agent persistent memory — `.claude/agent-memory/<agent>/MEMORY.md`.

Each INERTIA agent keeps a durable, human-readable memory that survives across
sessions: lessons, conventions, gotchas it has learned about THIS project. The
forge stores it; the agent reads and appends to it. Deterministic file I/O.
"""
from __future__ import annotations

import argparse
from pathlib import Path

MEM_ROOT = Path(".claude") / "agent-memory"


def _path(agent: str) -> Path:
    return MEM_ROOT / agent / "MEMORY.md"


def ensure(agent: str) -> Path:
    """Create the agent's memory file (with a header) if absent."""
    p = _path(agent)
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"# {agent} — memory\n\nDurable lessons this agent has learned "
                     f"about this project.\n\n", encoding="utf-8")
    return p


def add(agent: str, note: str, tags: list[str] | None = None) -> None:
    ensure(agent)
    line = f"- {note}" + (f"  _[{', '.join(tags)}]_" if tags else "") + "\n"
    with open(_path(agent), "a", encoding="utf-8") as f:
        f.write(line)


def show(agent: str) -> str | None:
    p = _path(agent)
    return p.read_text(encoding="utf-8") if p.exists() else None


def agents_with_memory() -> list[str]:
    if not MEM_ROOT.exists():
        return []
    return sorted(d.name for d in MEM_ROOT.iterdir() if (d / "MEMORY.md").exists())


def run_memory(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge memory")
    sub = p.add_subparsers(dest="sub", required=True)
    a = sub.add_parser("add")
    a.add_argument("agent")
    a.add_argument("note", nargs="+")
    a.add_argument("--tag", action="append", default=[], dest="tags")
    sh = sub.add_parser("show"); sh.add_argument("agent")
    sub.add_parser("list")
    args = p.parse_args(argv)
    if args.sub == "add":
        add(args.agent, " ".join(args.note), args.tags)
        print(f"remembered for {args.agent}")
        return 0
    if args.sub == "show":
        text = show(args.agent)
        if text is None:
            print(f"no memory for {args.agent}")
            return 1
        print(text)
        return 0
    mem = agents_with_memory()
    print("\n".join(f"  {a}" for a in mem) if mem else "(no agent memory yet)")
    return 0
