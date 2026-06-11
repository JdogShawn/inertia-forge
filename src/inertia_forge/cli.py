"""inertia-forge command-line interface.

  inertia-forge init [--target DIR]   install Claude Code hooks into a project
  inertia-forge skills                 list registered skills + evidence modes
  inertia-forge start <skill> <target> start a forge session
  inertia-forge record-phase <p> <t>   record a phase (auto-closes on all-green)
  inertia-forge status                 show the active session
  inertia-forge close                  close (refuses while gates remain)
"""
from __future__ import annotations

import sys


def _list_skills() -> int:
    from inertia_forge.skill_registry import (
        get_all_skills,
        get_evidence_mode,
        get_required_steps,
    )
    for name in sorted(get_all_skills()):
        mode = get_evidence_mode(name)
        gates = get_required_steps(name)
        print(f"  {name:26} {mode:15} blocking_gates={gates}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if argv and argv[0] == "init":
        from inertia_forge.init import run_init
        return run_init(argv[1:])
    if argv and argv[0] == "task":
        from inertia_forge.task_cli import run_task
        return run_task(argv[1:])
    if argv and argv[0] in ("skills", "list"):
        return _list_skills()

    # Delegate forge operations (start / record-phase / status / close) to the
    # bridge CLI — the single sanctioned entry point for session lifecycle.
    from inertia_forge.skill_bridge import main as bridge_main
    return bridge_main(argv)


if __name__ == "__main__":
    sys.exit(main())
