"""Targeted tests — run only the tests for what changed, not the whole suite.

Maps changed source files to their conventional test path
(``[src/]<pkg>/<path>/<mod>.py`` → ``tests/<path>/test_<mod>.py``) using git's
staged + unstaged diff, then turns the targets into a one-line driver
instruction. Pure path math over ``git diff`` — deterministic, no LLM.
"""
from __future__ import annotations

import subprocess
from pathlib import Path, PurePosixPath


def map_source_to_test(source_path: str) -> str | None:
    """Conventional test path for a source file, or None if it has none.

    Skips ``__init__.py``, existing test files, and traversal paths. Strips a
    leading ``src/`` and the top-level package directory.
    """
    p = PurePosixPath(source_path)
    if p.suffix != ".py" or p.name == "__init__.py" or p.name.startswith("test_"):
        return None
    if ".." in p.parts:
        return None
    parts = list(p.parts)
    if parts and parts[0] == "src":
        parts = parts[1:]
    if len(parts) >= 2:  # drop the package directory
        parts = parts[1:]
    sub, stem = parts[:-1], PurePosixPath(parts[-1]).stem
    if sub:
        return f"tests/{'/'.join(sub)}/test_{stem}.py"
    return f"tests/test_{stem}.py"


def _git_changed(project_root: Path, extra: list[str]) -> list[str]:
    try:
        r = subprocess.run(
            ["git", "diff", "--name-only", *extra], cwd=str(project_root),
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace", check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def resolve_test_targets(project_root: Path) -> list[str]:
    """Existing conventional test paths for staged + unstaged source changes."""
    seen: set[str] = set()
    targets: list[str] = []
    for line in _git_changed(project_root, ["--cached"]) + _git_changed(project_root, []):
        test_path = map_source_to_test(line)
        if test_path and test_path not in seen and (project_root / test_path).exists():
            seen.add(test_path)
            targets.append(test_path)
    return targets


def build_test_instruction(targets: list[str]) -> str:
    """One-line driver instruction naming the targeted tests, or '' if none."""
    if not targets:
        return ""
    return f"Run only these tests: pytest {' '.join(targets)} -v --tb=short"
