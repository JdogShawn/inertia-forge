"""Top-level CLI commands: arch, verify, status, state.

These expose the deterministic engines (the analyzer, the task/state stores) as
standalone commands — no bpsai-pair required.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


# ── shared ───────────────────────────────────────────────────────────
def _print_findings(findings: list[dict]) -> int:
    """Print findings grouped by severity. Return 1 if any P0, else 0."""
    by_sev: dict[str, list[dict]] = {"P0": [], "P1": [], "P2": []}
    for f in findings:
        by_sev.setdefault(f.get("severity", "P2"), []).append(f)
    if not findings:
        print("✓ no findings")
        return 0
    for sev in ("P0", "P1", "P2"):
        for f in by_sev.get(sev, []):
            print(f"  [{sev}] {f.get('message', '')}")
    p0, p1, p2 = (len(by_sev[s]) for s in ("P0", "P1", "P2"))
    print(f"\n{p0} P0, {p1} P1, {p2} P2")
    return 1 if p0 else 0


# ── arch ─────────────────────────────────────────────────────────────
def run_arch(argv: list[str]) -> int:
    """inertia-forge arch <path> [path...] — deterministic architecture check."""
    from inertia_forge.independent_analyzer import analyze_directory, analyze_file

    parser = argparse.ArgumentParser(prog="inertia-forge arch")
    parser.add_argument("paths", nargs="+", help="files or directories to check")
    args = parser.parse_args(argv)
    findings: list[dict] = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            findings += analyze_directory(path)
        elif path.is_file():
            findings += analyze_file(path)
        else:
            print(f"  [P1] path not found: {p}")
    return _print_findings(findings)


# ── verify ───────────────────────────────────────────────────────────
def run_verify(argv: list[str]) -> int:
    """inertia-forge verify [dir] — run pytest, report pass/fail/coverage."""
    from inertia_forge.independent_analyzer import parse_pytest_summary

    parser = argparse.ArgumentParser(prog="inertia-forge verify")
    parser.add_argument("target", nargs="?", default=".", help="test dir (default: .)")
    parser.add_argument("--cov", metavar="PKG", help="measure coverage of PKG (needs pytest-cov)")
    args = parser.parse_args(argv)
    cmd = [sys.executable, "-m", "pytest", args.target, "--tb=short", "-q"]
    if args.cov:
        cmd += [f"--cov={args.cov}", "--cov-report=term-missing"]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except FileNotFoundError:
        print("pytest not available — `pip install pytest`", file=sys.stderr)
        return 1
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr.strip():
        print(result.stderr, end="", file=sys.stderr)
    s = parse_pytest_summary(result.stdout + result.stderr)
    cov = f" · coverage {s['coverage']}%" if s["coverage"] is not None else ""
    print(f"\nVERIFY: {s['passed']} passed · {s['failed']} failed · "
          f"{s['errors']} errors{cov}")
    return result.returncode


# ── state ────────────────────────────────────────────────────────────
def run_state(argv: list[str]) -> int:
    """inertia-forge state [--done ...] [--next ...] — continuity ledger."""
    from inertia_forge import state as st

    parser = argparse.ArgumentParser(prog="inertia-forge state")
    parser.add_argument("--done", default="", help="what was just done")
    parser.add_argument("--next", dest="next_", default="", help="what's next")
    parser.add_argument("--log", action="store_true", help="show recent history")
    args = parser.parse_args(argv)
    if args.done or args.next_:
        st.set_progress(args.done, args.next_)
    data = st.load()
    if args.log:
        hist = data["history"][-10:]
        if not hist:
            print("(no history)")
        for h in hist:
            print(f"- done: {h['done'] or '(none)'}")
            print(f"  next: {h['next'] or '(none)'}")
        return 0
    print(f"last: {data['last'] or '(none)'}")
    print(f"next: {data['next'] or '(none)'}")
    return 0


# ── status ───────────────────────────────────────────────────────────
def run_status(_argv: list[str]) -> int:
    """inertia-forge status — forge session + plan/tasks + last/next rollup."""
    from inertia_forge import state as st, tasks as tk
    from inertia_forge.completion_lock import get_forge_status

    forge = get_forge_status() or "no active session"
    print(f"forge:  {forge}")

    plan = tk.get_plan()
    print(f"plan:   {plan['type'] + ' — ' + plan['title'] if plan else '(none)'}")

    tasks = tk.list_tasks()
    if tasks:
        done = sum(1 for t in tasks if t["status"] == "done")
        ac_met = sum(1 for t in tasks for c in t["acceptance_criteria"] if c["done"])
        ac_tot = sum(len(t["acceptance_criteria"]) for t in tasks)
        active = tk.active_task_id() or "(none)"
        print(f"tasks:  {done}/{len(tasks)} done · AC {ac_met}/{ac_tot} · active {active}")
    else:
        print("tasks:  (none)")

    data = st.load()
    print(f"last:   {data['last'] or '(none)'}")
    print(f"next:   {data['next'] or '(none)'}")
    return 0
