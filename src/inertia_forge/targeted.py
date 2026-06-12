"""Targeted test selection — map changed source files to the tests that cover them.

Given changed files (explicit args, or from `git diff`), resolve the test files
by naming convention (``pkg/foo.py`` → ``tests/test_foo.py`` or
``tests/<sub>/test_foo.py``) and keep the ones that exist. Lets CI run only what
a change can break, instead of the whole suite. Deterministic; git is optional.
"""
from __future__ import annotations

import subprocess
from pathlib import Path, PurePosixPath


def candidates(source: str) -> list[str]:
    """Candidate test-file paths for a changed source file (may not exist)."""
    p = PurePosixPath(source.replace("\\", "/"))
    if p.suffix != ".py" or p.name.startswith("test_") or p.name == "__init__.py":
        return []
    stem = p.stem
    parts = [seg for seg in p.parts if seg not in ("src",)]
    out = [f"tests/test_{stem}.py"]
    if len(parts) > 2:  # has an intermediate package path
        sub = "/".join(parts[1:-1])
        out.append(f"tests/{sub}/test_{stem}.py")
    return out


def existing_targets(changed: list[str], root: Path) -> list[str]:
    """The subset of candidate tests that actually exist on disk (de-duped)."""
    seen: list[str] = []
    for f in changed:
        for cand in candidates(f):
            if cand not in seen and (root / cand).exists():
                seen.append(cand)
    return seen


def git_changed(root: Path, ref: str) -> list[str]:
    """Files changed vs *ref* via `git diff --name-only`; [] if git unavailable."""
    try:
        r = subprocess.run(["git", "diff", "--name-only", ref], cwd=str(root),
                           capture_output=True, text=True, timeout=10)
        return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    except (OSError, subprocess.SubprocessError):
        return []


def run_targeted(argv: list[str]) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="inertia-forge targeted")
    parser.add_argument("files", nargs="*", help="changed files (default: git diff)")
    parser.add_argument("--since", default="HEAD", help="git ref to diff against")
    args = parser.parse_args(argv)
    root = Path(".")
    changed = args.files or git_changed(root, args.since)
    targets = existing_targets(changed, root)
    if not targets:
        print("(no matching test files for the changed sources)")
        return 0
    for tgt in targets:
        print(tgt)
    return 0
