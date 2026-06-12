"""Preflight — one gate that answers "are we ready to work / ship?".

Composes the forge's deterministic checks into a single pass: a clean working
tree (churn-filtered), an active plan with tasks, no architecture P0s, no
task-store drift, and — optionally — green tests. Each check reports
PASS / WARN / FAIL; `preflight` exits 1 on any FAIL. The pre-work / pre-ship
checklist, mechanized.
"""
from __future__ import annotations

import argparse
from pathlib import Path

Check = tuple[str, str, str]  # (name, status, detail); status in PASS/WARN/FAIL


def _check_git() -> Check:
    from inertia_forge.gitcheck import dirty_files
    dirty = dirty_files(Path("."))
    return ("git", "PASS" if not dirty else "WARN",
            "clean" if not dirty else f"{len(dirty)} uncommitted non-churn file(s)")


def _check_plan() -> Check:
    from inertia_forge import tasks as tk
    plan = tk.get_plan()
    if not plan:
        return ("plan", "WARN", "no active plan")
    n = len(tk.list_tasks())
    return ("plan", "PASS" if n else "WARN", f"{plan['type']} — {n} task(s)")


def _check_arch(path: str) -> Check:
    from inertia_forge.independent_analyzer import analyze_directory
    p = Path(path)
    if not p.exists():
        return ("arch", "WARN", f"no source dir at {path!r} (use --path)")
    p0 = [f for f in analyze_directory(p) if f.get("severity") == "P0"]
    return ("arch", "PASS" if not p0 else "FAIL", "0 P0" if not p0 else f"{len(p0)} P0")


def _check_consistency() -> Check:
    from inertia_forge.consistency import issues
    iss = issues()
    return ("consistency", "PASS" if not iss else "FAIL",
            "clean" if not iss else f"{len(iss)} issue(s)")


def run_preflight(argv: list[str]) -> int:
    from inertia_forge.glyphs import g, seal
    from inertia_forge.palette import paint
    p = argparse.ArgumentParser(prog="inertia-forge preflight")
    p.add_argument("--path", default="src", help="source dir for the arch check")
    p.add_argument("--tests", help="also run pytest on this dir")
    args = p.parse_args(argv)

    checks = [_check_git(), _check_plan(), _check_arch(args.path), _check_consistency()]
    if args.tests:
        from inertia_forge.commands import run_verify
        rc = run_verify([args.tests])
        checks.append(("tests", "PASS" if rc == 0 else "FAIL",
                       "green" if rc == 0 else "failing"))
    kind = {"PASS": "ok", "WARN": "warn", "FAIL": "error"}
    for name, status, detail in checks:
        print(f"  {seal(kind[status])} {paint(name.ljust(12), 'text')} {paint(detail, 'muted')}")
    fails = sum(1 for _, s, _ in checks if s == "FAIL")
    warns = sum(1 for _, s, _ in checks if s == "WARN")
    verb = "NOT READY" if fails else "ready"
    print(f"{seal('error' if fails else 'ok')} {verb} "
          f"{g('dot')} {fails} fail {g('dot')} {warns} warn")
    return 1 if fails else 0
