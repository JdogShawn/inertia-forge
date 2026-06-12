"""Change-scope enforcement — keep work inside a task's declared paths.

A task can carry a ``scope`` of path prefixes or globs. `scope set <id> --paths …`
declares it; `scope check` compares the working-tree diff against the ACTIVE
task's scope and flags any file changed outside it. Deterministic drift
detection — it catches an agent wandering out of bounds.
"""
from __future__ import annotations

import argparse
import fnmatch
import subprocess
from pathlib import Path

from inertia_forge import tasks as t


def _changed(root: Path) -> list[str]:
    from inertia_forge.gitcheck import _is_churn
    try:
        r = subprocess.run(["git", "status", "--porcelain"], cwd=str(root),
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return []
    files = [ln[3:].strip().strip('"') for ln in r.stdout.splitlines() if ln[3:].strip()]
    return [f for f in files if not _is_churn(f)]


def in_scope(path: str, scope: list[str]) -> bool:
    """True if *path* sits under any scope entry (glob or path prefix)."""
    for s in scope:
        if "*" in s or "?" in s:
            if fnmatch.fnmatch(path, s):
                return True
        elif path == s or path.startswith(s.rstrip("/") + "/"):
            return True
    return False


def out_of_scope(changed: list[str], scope: list[str]) -> list[str]:
    return [f for f in changed if not in_scope(f, scope)] if scope else []


def run_scope(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge scope")
    sub = p.add_subparsers(dest="sub", required=True)
    s = sub.add_parser("set", help="declare a task's scope")
    s.add_argument("id"); s.add_argument("--paths", nargs="+", required=True)
    sub.add_parser("check", help="flag changes outside the active task's scope")
    args = p.parse_args(argv)

    if args.sub == "set":
        t.update_task(args.id, scope=args.paths)
        print(f"{args.id} scope: {', '.join(args.paths)}")
        return 0

    active = t.active_task_id()
    task = t.get_task(active) if active else None
    if not task:
        print("(no active task — `task start <id>` first)")
        return 0
    scope = task.get("scope", [])
    if not scope:
        print(f"(active task {active} has no declared scope — `scope set {active} --paths …`)")
        return 0
    oos = out_of_scope(_changed(Path(".")), scope)
    if not oos:
        print(f"{seal('ok')} all changes within scope of {active}")
        return 0
    for f in oos:
        print(f"{seal('warn')} out of scope: {f}")
    return 1
