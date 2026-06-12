"""Structured diff view — what changed, by file, lines, and role.

Parses ``git diff --numstat`` into per-file (added, removed, path, role)
records and rolls them up. `diff [--since ref]` gives an agent (or you) a
structured read of a change set — the same view that feeds review, targeted
tests, and scope. Deterministic; git optional (no repo → no changes).
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def parse_numstat(text: str) -> list[dict]:
    """Parse `git diff --numstat` output into per-file records."""
    out: list[dict] = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, removed, path = parts
        out.append({"added": int(added) if added.isdigit() else 0,
                    "removed": int(removed) if removed.isdigit() else 0,
                    "path": path})
    return out


def with_roles(files: list[dict]) -> list[dict]:
    from inertia_forge.roles import detect
    for f in files:
        f["role"] = detect(f["path"])
    return files


def git_numstat(root: Path, ref: str) -> str:
    try:
        r = subprocess.run(["git", "diff", "--numstat", ref], cwd=str(root),
                           capture_output=True, text=True, timeout=10)
        return r.stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def run_diff(argv: list[str]) -> int:
    from inertia_forge.palette import paint
    p = argparse.ArgumentParser(prog="inertia-forge diff")
    p.add_argument("--since", default="HEAD", help="git ref to diff against")
    args = p.parse_args(argv)
    files = with_roles(parse_numstat(git_numstat(Path("."), args.since)))
    if not files:
        print("(no changes)")
        return 0
    from inertia_forge.glyphs import g
    by_role: dict[str, int] = {}
    add = rem = 0
    for f in files:
        plus = paint(f"+{f['added']}", "success")
        minus = paint(f"-{f['removed']}", "error")
        role = paint(f["role"].ljust(7), "muted")
        print(f"  {plus} {minus}  {role} {f['path']}")
        by_role[f["role"]] = by_role.get(f["role"], 0) + 1
        add += f["added"]
        rem += f["removed"]
    roles = ", ".join(f"{k}:{v}" for k, v in sorted(by_role.items()))
    dot = paint(g("dot"), "muted")
    print(f"\n{len(files)} file(s) {dot} {paint(f'+{add}', 'success')} "
          f"{paint(f'-{rem}', 'error')} {dot} {roles}")
    return 0
