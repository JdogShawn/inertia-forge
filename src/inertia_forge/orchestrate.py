"""Deterministic command pipeline — run forge commands in sequence, fail-fast.

A no-LLM 'orchestrate': compose gates/commands into one ordered pipeline that
stops at the first failure. e.g.

    inertia-forge orchestrate "arch src/" "verify tests/" "sweep src/"

Each step is a forge subcommand string; the pipeline's exit code is the first
non-zero step's (0 if all pass). Use forward-slash paths in steps — they work
on every OS, and shlex (POSIX) would eat Windows backslashes.
"""
from __future__ import annotations

import argparse
import shlex


def _select_agent(argv: list[str]) -> int:
    """orchestrate select-agent "<task description>" — deterministically map a
    task to the best-fit agent via the skill recommender."""
    desc = " ".join(argv).strip()
    if not desc:
        print("usage: orchestrate select-agent \"<task description>\"")
        return 1
    from inertia_forge.recommend import search
    hits = search(desc)
    if hits:
        top = hits[0]
        print(f"agent: {top.get('agent', 'Piston')}  "
              f"(skill: {top['skill']}, score {top['score']})")
    else:
        print("agent: Piston  (default — no skill matched)")
    return 0


def run_orchestrate(argv: list[str]) -> int:
    if argv and argv[0] == "select-agent":
        return _select_agent(argv[1:])
    parser = argparse.ArgumentParser(prog="inertia-forge orchestrate")
    parser.add_argument("steps", nargs="+", help='forge command strings, e.g. "arch src/"')
    parser.add_argument("--keep-going", action="store_true",
                        help="run every step even if one fails (report worst exit)")
    args = parser.parse_args(argv)

    from inertia_forge.cli import main as forge_main

    worst = 0
    for step in args.steps:
        print(f"\n== {step} ==")
        rc = forge_main(shlex.split(step))
        if rc != 0:
            worst = rc
            if not args.keep_going:
                print(f"\nPIPELINE FAILED at: {step}")
                return rc
    print("\nPIPELINE OK" if worst == 0 else f"\nPIPELINE FAILED (worst exit {worst})")
    return worst
