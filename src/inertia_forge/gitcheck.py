"""Git-aware verification — a clean tree and a commit that names its work.

Deterministic post-commit checks: after work lands, the working tree should be
clean once *churn* is ignored (caches, coverage, forge runtime state), and the
HEAD commit should reference a task id (``T<sprint>.<seq>``). `verify-commit`
surfaces violations and exits 1 so a finish step can gate on it. Git is optional
— outside a repo there's nothing to verify, which counts as clean.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

TASK_ID_RE = re.compile(r"\bT\d+\.\d+\b")

# Substrings that mark a path as churn — never block a commit over these.
CHURN = (".forge/", "__pycache__/", ".pytest_cache/", ".coverage", ".egg-info",
         ".ds_store", "/heartbeat", "telemetry/", "node_modules/", ".mypy_cache/")


def _git(root: Path, *args: str) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=str(root), capture_output=True,
                           text=True, timeout=10)
        return r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def _is_churn(path: str) -> bool:
    low = path.lower()
    return any(c in low for c in CHURN)


def dirty_files(root: Path) -> list[str]:
    """Uncommitted, non-churn files from `git status --porcelain`."""
    out = _git(root, "status", "--porcelain")
    files = []
    for line in out.splitlines():
        f = line[3:].strip().strip('"')
        if f and not _is_churn(f):
            files.append(f)
    return files


def meaningful_changes(root: Path, ref: str) -> tuple[list[str], list[str]]:
    """(meaningful, other) changed files vs *ref* — churn filtered, untracked
    included. Meaningful = code/test/cli (real work); other = doc/config/data."""
    from inertia_forge.roles import detect
    diff = _git(root, "diff", "--name-only", ref)
    untracked = _git(root, "ls-files", "--others", "--exclude-standard")
    seen: list[str] = []
    for f in (diff + "\n" + untracked).splitlines():
        f = f.strip()
        if f and f not in seen and not _is_churn(f):
            seen.append(f)
    meaningful = [f for f in seen if detect(f) in ("source", "test", "cli")]
    return meaningful, [f for f in seen if f not in meaningful]


def run_verify_output(argv: list[str]) -> int:
    import argparse
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge verify-output")
    p.add_argument("--since", default="HEAD", help="git ref to diff against")
    args = p.parse_args(argv)
    meaningful, other = meaningful_changes(Path("."), args.since)
    if meaningful:
        print(f"{seal('ok')} {len(meaningful)} meaningful change(s): {', '.join(meaningful[:5])}")
        return 0
    if other:
        print(f"{seal('warn')} only metadata/doc/config changed, no code or tests: "
              f"{', '.join(other[:5])}")
        return 1
    print(f"{seal('warn')} no changes vs {args.since} — produced no output")
    return 1


def head_subject(root: Path) -> str:
    return _git(root, "log", "-1", "--format=%s").strip()


def head_task(root: Path) -> str | None:
    """The task id referenced by the HEAD commit subject, if any."""
    m = TASK_ID_RE.search(head_subject(root))
    return m.group(0) if m else None


def verify(root: Path, require_task: bool) -> list[str]:
    """Every commit-verification problem as human-readable lines."""
    issues = []
    dirty = dirty_files(root)
    if dirty:
        issues.append(f"working tree has {len(dirty)} uncommitted non-churn "
                      f"file(s): {', '.join(dirty[:5])}")
    if require_task and _git(root, "rev-parse", "HEAD") and not head_task(root):
        issues.append("HEAD commit does not reference a task id "
                      f"(T<sprint>.<seq>): {head_subject(root)!r}")
    return issues


def run_verify_commit(argv: list[str]) -> int:
    import argparse
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge verify-commit")
    p.add_argument("--require-task", action="store_true",
                   help="HEAD commit must reference a task id")
    args = p.parse_args(argv)
    issues = verify(Path("."), args.require_task)
    if not issues:
        suffix = " + task reference" if args.require_task else ""
        print(f"{seal('ok')} commit verified — clean tree{suffix}")
        return 0
    for msg in issues:
        print(f"{seal('error')} {msg}")
    return 1
