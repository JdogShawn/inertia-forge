"""Top-level CLI commands: arch, verify, status, state.

These expose the deterministic engines (the analyzer, the task/state stores) as
standalone commands — no bpsai-pair required.
"""
from __future__ import annotations

import argparse
import re
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
        print("OK: no findings")
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


# ── log (audit trail) ────────────────────────────────────────────────
def run_log(argv: list[str]) -> int:
    """inertia-forge log [-n N] [--claims] — view the forge audit trail."""
    from inertia_forge.bypass_prevention import read_behavioral_log

    parser = argparse.ArgumentParser(prog="inertia-forge log")
    parser.add_argument("-n", type=int, default=20, help="entries to show")
    parser.add_argument("--claims", action="store_true", help="show the claims log")
    args = parser.parse_args(argv)
    if args.claims:
        p = Path(".forge") / "claims.jsonl"
        lines = p.read_text(encoding="utf-8").splitlines()[-args.n:] if p.exists() else []
        print("\n".join(lines) if lines else "(no claims)")
        return 0
    entries = read_behavioral_log(args.n)
    if not entries:
        print("(no audit events)")
        return 0
    for e in entries:
        print(f"{e.get('timestamp', '?')}  {e.get('type', '?')}: {e.get('details', '')}")
    return 0


# ── read (mark methodology doc read) ─────────────────────────────────
def run_read(argv: list[str]) -> int:
    """inertia-forge read <skill> — mark the skill's methodology doc as read."""
    from inertia_forge.doc_reading import mark_read
    from inertia_forge.skill_registry import get_skill, validate_skill_name

    parser = argparse.ArgumentParser(prog="inertia-forge read")
    parser.add_argument("skill")
    args = parser.parse_args(argv)
    if not validate_skill_name(args.skill):
        print(f"unknown skill: {args.skill}")
        return 1
    doc = get_skill(args.skill).doc
    if doc and not Path(doc).is_file():
        print(f"declared doc not found: {doc}")
        return 1
    mark_read(args.skill)
    print(f"marked {args.skill} as read" + (f" ({doc})" if doc else ""))
    return 0


# ── pack (context handoff) ───────────────────────────────────────────
def run_pack(_argv: list[str]) -> int:
    """inertia-forge pack — bundle state + plan + tasks + audit to .forge/context_pack.md."""
    from inertia_forge import state as st, tasks as tk
    from inertia_forge.bypass_prevention import read_behavioral_log
    from inertia_forge.completion_lock import get_forge_status

    plan = tk.get_plan()
    lines = ["# Forge Context Pack", "",
             f"**Forge:** {get_forge_status() or 'no active session'}",
             f"**Plan:** {plan['type'] + ' — ' + plan['title'] if plan else '(none)'}"]
    tasks = tk.list_tasks()
    if tasks:
        lines.append("\n## Tasks")
        for x in tasks:
            met = sum(1 for c in x["acceptance_criteria"] if c["done"])
            lines.append(f"- {x['id']} [{x['status']}] AC {met}/{len(x['acceptance_criteria'])} — {x['title']}")
    data = st.load()
    lines += ["", "## Continuity", f"- last: {data['last'] or '(none)'}",
              f"- next: {data['next'] or '(none)'}"]
    audit = read_behavioral_log(10)
    if audit:
        lines += ["", "## Recent audit"] + [f"- {e.get('type')}: {e.get('details')}" for e in audit]
    out = Path(".forge") / "context_pack.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


# ── check (project-level gate — beyond skills) ───────────────────────
_SECRET_RE = re.compile(
    r"(password|secret|api[_-]?key|access[_-]?token|auth[_-]?token|token)\s*[:=]\s*['\"][^'\"]{6,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"            # PEM private key
    r"|AKIA[0-9A-Z]{16}"                              # AWS access key id
    r"|pypi-[A-Za-z0-9_-]{16,}"                       # PyPI API token
    r"|gh[pousr]_[A-Za-z0-9]{30,}"                    # GitHub token
    r"|xox[baprs]-[A-Za-z0-9-]{10,}"                  # Slack token
    r"|AIza[A-Za-z0-9_-]{30,}"                        # Google API key
    r"|sk_live_[A-Za-z0-9]{20,}"                      # Stripe live key
    r"|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{6,}",  # JWT
    re.IGNORECASE,
)
_SCAN_SUFFIXES = {".py", ".env", ".yaml", ".yml", ".json", ".toml", ".sh", ".cfg", ".ini"}


def _scan_secrets(path: Path) -> list[dict]:
    files = [path] if path.is_file() else [
        f for f in path.rglob("*")
        if f.suffix in _SCAN_SUFFIXES
        and not any(skip in str(f) for skip in (".forge", "__pycache__", ".git"))
    ]
    findings: list[dict] = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if not line.strip().startswith("#") and _SECRET_RE.search(line):
                findings.append({"severity": "P0", "rule": "possible_secret",
                                 "file": str(f), "line": i,
                                 "message": f"{f.name}:{i}: possible hardcoded secret"})
    return findings


def run_check(argv: list[str]) -> int:
    """inertia-forge check [path] [--tests DIR] — project gate: arch + secrets (+ tests).

    A session-less quality gate (pre-commit / CI), enforcing project invariants
    rather than a skill's methodology — the forge beyond skills.
    """
    from inertia_forge.independent_analyzer import analyze_directory, analyze_file

    parser = argparse.ArgumentParser(prog="inertia-forge check")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--tests", help="also run pytest on this dir")
    parser.add_argument("--deps", action="store_true", help="also audit dependencies (pip-audit)")
    args = parser.parse_args(argv)
    p = Path(args.path)
    findings = (analyze_directory(p) if p.is_dir() else analyze_file(p)) + _scan_secrets(p)
    rc = _print_findings(findings)
    if args.tests:
        print("\n-- tests --")
        if run_verify([args.tests]) != 0:
            rc = 1
    if args.deps:
        print("\n-- dependencies --")
        if _scan_deps(p) != 0:
            rc = 1
    return rc


def _scan_deps(path: Path) -> int:
    """Audit dependencies via pip-audit (optional). Returns its exit code, or 0
    if pip-audit isn't installed (a missing optional tool shouldn't fail a gate)."""
    import importlib.util
    if importlib.util.find_spec("pip_audit") is None:
        print("scan-deps: pip-audit not installed (optional) — `pip install pip-audit`")
        return 0
    cmd = [sys.executable, "-m", "pip_audit", "--progress-spinner=off"]
    req = path / "requirements.txt"
    if req.is_file():
        cmd += ["-r", str(req)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=300)
    except (subprocess.TimeoutExpired, OSError):
        print("scan-deps: pip-audit failed to run", file=sys.stderr)
        return 0
    print(result.stdout, end="")
    if result.stderr.strip():
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


def run_scan_deps(argv: list[str]) -> int:
    """inertia-forge scan-deps [path] — dependency vulnerability scan (pip-audit)."""
    parser = argparse.ArgumentParser(prog="inertia-forge scan-deps")
    parser.add_argument("path", nargs="?", default=".")
    args = parser.parse_args(argv)
    return _scan_deps(Path(args.path))
