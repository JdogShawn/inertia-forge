"""Release management — version consistency + readiness checklist. Zero LLM.

`validate-versions` is the one I most needed: it scans pyproject.toml and the
package `__version__` and fails if they disagree (the bug that bit every manual
release). `checklist` runs the full readiness gate.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def find_versions() -> dict[str, str]:
    """Map of source-of-truth file -> declared version string."""
    out: dict[str, str] = {}
    py = Path("pyproject.toml")
    if py.exists():
        m = re.search(r'^version\s*=\s*["\'](.+?)["\']', py.read_text(encoding="utf-8"), re.M)
        if m:
            out["pyproject.toml"] = m.group(1)
    root = Path("src") if Path("src").exists() else Path(".")
    for init in sorted(root.rglob("__init__.py")):
        if "__pycache__" in str(init):
            continue
        m = re.search(r'__version__\s*=\s*["\'](.+?)["\']', init.read_text(encoding="utf-8"))
        if m:
            out[str(init)] = m.group(1)
            break
    return out


def versions_consistent() -> tuple[bool, dict[str, str]]:
    v = find_versions()
    return (len(set(v.values())) <= 1), v


def _validate_versions() -> int:
    ok, v = versions_consistent()
    if not v:
        print("no version declarations found")
        return 1
    for src, ver in v.items():
        print(f"  {ver:12} {src}")
    print("OK: versions consistent" if ok else "MISMATCH: versions disagree")
    return 0 if ok else 1


def _release_checks() -> list[tuple[str, str, str]]:
    """[(name, status, detail)] — a real release-readiness gate. PASS/WARN/FAIL."""
    import subprocess
    import sys
    from inertia_forge.freshness import is_stale
    from inertia_forge.gitcheck import dirty_files
    checks: list[tuple[str, str, str]] = []
    ok, v = versions_consistent()
    ver = next(iter(v.values()), "?")
    checks.append(("versions", "PASS" if ok else "FAIL",
                   "consistent" if ok else "disagree: " + ", ".join(f"{k.split('/')[-1]}={x}" for k, x in v.items())))
    dirty = dirty_files(Path("."))
    checks.append(("git", "PASS" if not dirty else "WARN",
                   "clean" if not dirty else f"{len(dirty)} uncommitted file(s)"))
    changelog = Path("CHANGELOG.md")
    if changelog.exists():
        has = ver in changelog.read_text(encoding="utf-8")
        checks.append(("changelog", "PASS" if has else "FAIL",
                       f"v{ver} present" if has else f"no entry for v{ver}"))
    else:
        checks.append(("changelog", "WARN", "no CHANGELOG.md (use `changelog` for git notes)"))
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q"],
                           capture_output=True, text=True, timeout=180)
        rc = r.returncode
        if rc == 0:
            checks.append(("tests", "PASS", "collectable"))
        elif rc == 5:  # pytest's "no tests collected" — not a failure
            checks.append(("tests", "WARN", "no tests found"))
        else:
            checks.append(("tests", "FAIL", "collection failed"))
    except (OSError, subprocess.SubprocessError):
        checks.append(("tests", "WARN", "pytest not runnable"))
    stale = is_stale("README.md", 30)
    checks.append(("docs", "WARN" if stale else "PASS",
                   "README >30d or missing" if stale else "README fresh"))
    return checks


def _checklist() -> int:
    from inertia_forge.glyphs import seal
    from inertia_forge.palette import paint
    checks = _release_checks()
    kind = {"PASS": "ok", "WARN": "warn", "FAIL": "error"}
    for name, status, detail in checks:
        print(f"  {seal(kind[status])} {paint(name.ljust(12), 'text')} {paint(detail, 'muted')}")
    fails = sum(1 for _, s, _ in checks if s == "FAIL")
    verb = "NOT release-ready" if fails else "release-ready"
    print(f"\n{seal('error' if fails else 'ok')} {verb} ({fails} blocker(s))")
    return 1 if fails else 0


def run_release(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge release")
    sub = p.add_subparsers(dest="sub", required=True)
    sub.add_parser("validate-versions")
    sub.add_parser("checklist")
    args = p.parse_args(argv)
    return _validate_versions() if args.sub == "validate-versions" else _checklist()
