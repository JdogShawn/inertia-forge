"""`inertia-forge feature <name>` — start a feature: branch + scaffold.

Deterministic git + task scaffolding (no LLM): creates a `feature/<slug>`
branch, a plan, a starter task (with acceptance criteria + verification), and
sets the continuity ledger's "next". Use `--no-branch` to scaffold without
touching git.
"""
from __future__ import annotations

import argparse
import re
import subprocess

from inertia_forge import config as cfg, state as st, tasks as t


def _git(*args: str) -> tuple[int, str]:
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return 127, "git not found on PATH"


def _slug(name: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", name.lower())).strip("-")


def run_feature(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge feature")
    p.add_argument("name", nargs="+", help="feature name")
    p.add_argument("--type", default="feature", choices=t.VALID_PLAN_TYPES)
    p.add_argument("--base", help="base branch to branch from")
    p.add_argument("--task-id", default="T1.1")
    p.add_argument("--no-branch", action="store_true", help="scaffold only, no git")
    args = p.parse_args(argv)
    name = " ".join(args.name)
    slug = _slug(name)

    if not args.no_branch:
        rc, _ = _git("rev-parse", "--is-inside-work-tree")
        if rc != 0:
            print("not a git repository — use --no-branch to scaffold only")
            return 1
        branch = f"feature/{slug}"
        cmd = ["checkout", "-b", branch] + ([args.base] if args.base else [])
        rc, out = _git(*cmd)
        if rc != 0:
            print(f"git: {out}")
            return 1
        print(f"branch:  {branch}")

    cx = float(cfg.get("default_complexity", 5))
    t.create_plan(args.type, f"Feature: {name}")
    t.add_task(args.task_id, f"Implement {name}", cx,
               [f"{name} implemented", "tests pass"], "pytest")
    st.set_progress(next_=f"implement {name}")
    print(f"plan:    {args.type} — Feature: {name}")
    print(f"task:    {args.task_id} (complexity {cx:g})")
    print(f"next:    implement {name}")
    return 0
