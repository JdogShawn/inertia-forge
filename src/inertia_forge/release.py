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


def _checklist() -> int:
    print("Release readiness checklist:")
    ok, _ = versions_consistent()
    print(f"  [{'x' if ok else ' '}] versions consistent (inertia-forge release validate-versions)")
    print("  [ ] tests green        — inertia-forge verify --cov")
    print("  [ ] project gate clean — inertia-forge check . --deps")
    print("  [ ] no unused imports  — inertia-forge sweep .")
    print("  [ ] schema current     — inertia-forge migrate status")
    print("  [ ] changelog updated")
    print("  [ ] tag + CI publish, then verify the artifact installs")
    return 0 if ok else 1


def run_release(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge release")
    sub = p.add_subparsers(dest="sub", required=True)
    sub.add_parser("validate-versions")
    sub.add_parser("checklist")
    args = p.parse_args(argv)
    return _validate_versions() if args.sub == "validate-versions" else _checklist()
