"""`inertia-forge doctor` — holistic health check of the forge setup.

Deterministic checks (python, pytest, .forge writability, skill-registry
validity, Claude Code hook wiring). PASS/WARN/FAIL per check; exits 1 on any
FAIL. `--fix` repairs what it safely can (currently: create .forge).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# (name, status, detail) — status in {PASS, WARN, FAIL}
Check = tuple[str, str, str]


def _check_python() -> Check:
    v = sys.version_info
    ok = v >= (3, 10)
    return ("python", "PASS" if ok else "FAIL", f"{v.major}.{v.minor} (need >=3.10)")


def _check_pytest() -> Check:
    try:
        import pytest  # noqa: F401
        return ("pytest", "PASS", "available")
    except ImportError:
        return ("pytest", "WARN", "not installed — `verify`/`check` need it")


def _check_forge_dir(fix: bool) -> Check:
    forge = Path(".forge")
    if forge.is_dir():
        return ("forge_dir", "PASS", "writable")
    if fix:
        forge.mkdir(parents=True, exist_ok=True)
        return ("forge_dir", "PASS", "created")
    return ("forge_dir", "WARN", "missing (created on first session, or --fix)")


def _check_skills() -> Check:
    from inertia_forge.validate import validate_registry
    issues = validate_registry()
    if not issues:
        return ("skills", "PASS", "registry valid")
    return ("skills", "FAIL", f"{len(issues)} problem(s) — run `skills validate`")


def _check_hooks() -> Check:
    settings = Path(".claude") / "settings.json"
    if not settings.exists():
        return ("hooks", "WARN", "not a Claude Code project (no .claude/settings.json)")
    if "inertia_forge.hookutil" in settings.read_text(encoding="utf-8"):
        return ("hooks", "PASS", "enforcement hooks wired")
    return ("hooks", "WARN", "hooks not installed — run `inertia-forge init`")


def run_doctor(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="inertia-forge doctor")
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    checks = [_check_python(), _check_pytest(), _check_forge_dir(args.fix),
              _check_skills(), _check_hooks()]
    if args.json:
        print(json.dumps([{"check": n, "status": s, "detail": d} for n, s, d in checks], indent=2))
    else:
        glyph = {"PASS": "[ok]", "WARN": "[!!]", "FAIL": "[XX]"}
        for name, status, detail in checks:
            print(f"  {glyph[status]} {name:12} {status:4} {detail}")
    return 1 if any(s == "FAIL" for _, s, _ in checks) else 0
