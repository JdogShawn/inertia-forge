"""Conventional-commit changelog — release notes from git history.

Parses ``git log`` subjects for Conventional Commits (feat / fix / perf /
refactor / docs / test / chore / build / ci / style / revert), groups them into
a markdown changelog, and surfaces breaking changes (a ``!`` before the colon).
Defaults to the range since the last tag. ASCII-clean output, deterministic —
reads only git.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

_CC = re.compile(
    r"^(?P<type>feat|fix|perf|refactor|docs|test|chore|build|ci|style|revert)"
    r"(?P<scope>\([^)]+\))?(?P<bang>!)?:\s*(?P<desc>.+)$")

_SECTIONS = [("feat", "Features"), ("fix", "Fixes"), ("perf", "Performance"),
             ("refactor", "Refactoring"), ("docs", "Docs"), ("test", "Tests"),
             ("build", "Build"), ("ci", "CI"), ("style", "Style"),
             ("revert", "Reverts"), ("chore", "Chores")]


def _git(root: Path, *args: str) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=str(root), capture_output=True,
                           text=True, timeout=15)
        return r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def git_subjects(root: Path, rng: str) -> list[str]:
    out = _git(root, "log", rng, "--format=%s", "--no-merges")
    return [ln for ln in out.splitlines() if ln.strip()]


def parse_commits(subjects: list[str]) -> tuple[dict[str, list[str]], list[str]]:
    """(grouped {type: [desc]}, breaking [desc]). Non-conventional → 'other'."""
    grouped: dict[str, list[str]] = {}
    breaking: list[str] = []
    for s in subjects:
        m = _CC.match(s)
        if not m:
            grouped.setdefault("other", []).append(s)
            continue
        scope = (m.group("scope") or "").strip("()")
        line = f"{scope}: {m.group('desc')}" if scope else m.group("desc")
        grouped.setdefault(m.group("type"), []).append(line)
        if m.group("bang"):
            breaking.append(line)
    return grouped, breaking


def render(grouped: dict[str, list[str]], breaking: list[str]) -> str:
    out = ["# Changelog", ""]
    if breaking:
        out += ["## Breaking changes", *[f"- {b}" for b in breaking], ""]
    for key, title in _SECTIONS:
        if grouped.get(key):
            out += [f"## {title}", *[f"- {d}" for d in grouped[key]], ""]
    if grouped.get("other"):
        out += ["## Other", *[f"- {d}" for d in grouped["other"]], ""]
    return "\n".join(out).rstrip() + "\n"


def run_changelog(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge changelog")
    p.add_argument("--since", help="start ref, exclusive (default: last tag)")
    p.add_argument("--until", default="HEAD", help="end ref (default: HEAD)")
    args = p.parse_args(argv)
    root = Path(".")
    since = args.since or _git(root, "describe", "--tags", "--abbrev=0").strip()
    rng = f"{since}..{args.until}" if since else args.until
    subjects = git_subjects(root, rng)
    if not subjects:
        print("(no commits in range)")
        return 0
    grouped, breaking = parse_commits(subjects)
    print(render(grouped, breaking))
    return 0
