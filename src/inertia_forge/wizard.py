"""Guided onboarding — `inertia-forge wizard`. Sets a project up end to end.

Non-interactive by design (so it works in any environment): installs the full
kit, runs a health check, and prints the loop. One command from empty repo to
forge-enforced.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def run_wizard(argv: list[str]) -> int:
    from inertia_forge.doctor import run_doctor
    from inertia_forge.init import run_init

    p = argparse.ArgumentParser(prog="inertia-forge wizard")
    p.add_argument("--target", default=".")
    args = p.parse_args(argv)
    root = Path(args.target)

    print("== INERTIA Forge — setup ==\n")
    if not (root / ".git").is_dir():
        print("  note: not a git repository yet — `git init` to enable branch/PR flow.\n")

    print("Installing the kit (hooks, agents, skills, commands, rules, memory, scaffold):")
    run_init(["--target", str(root)])

    print("\nHealth check:")
    run_doctor(["--fix"])

    print("\n== The loop ==")
    print("  /chart <goal>   plan      (Vector)")
    print("  /drive          implement (Piston, test-first)")
    print("  /calibrate      review    (Caliper)")
    print("  /launch         ship      (gate + PR)")
    print("  ...or /ignite <backlog.md> to start from a backlog.")
    print("\nKey commands: inertia-forge status | check | verify --cov | arch | sweep | gaps")
    print("Read the whole toolkit: inertia-forge capabilities")
    return 0
