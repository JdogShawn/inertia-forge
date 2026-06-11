"""inertia-forge command-line interface.

  inertia-forge init [--target DIR]   install Claude Code hooks into a project
  inertia-forge skills [validate]      list / validate the skill registry
  inertia-forge start <skill> <target> start a forge session
  inertia-forge record-phase <p> <t>   record a phase (auto-closes on all-green)
  inertia-forge status                 forge session + plan/tasks + last/next
  inertia-forge close                  close (refuses while gates remain)
  inertia-forge arch <path>            deterministic architecture check
  inertia-forge verify [dir]           run pytest on a target
  inertia-forge task ...               manage the native task store
  inertia-forge state [--done/--next]  session-continuity ledger
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

    cmd = argv[0] if argv else ""

    if cmd == "init":
        from inertia_forge.init import run_init
        return run_init(argv[1:])
    if cmd == "task":
        from inertia_forge.task_cli import run_task
        return run_task(argv[1:])
    if cmd in ("skills", "list"):
        if len(argv) > 1 and argv[1] == "validate":
            from inertia_forge.validate import run_validate
            return run_validate()
        return _list_skills()
    if cmd == "arch":
        from inertia_forge.commands import run_arch
        return run_arch(argv[1:])
    if cmd == "verify":
        from inertia_forge.commands import run_verify
        return run_verify(argv[1:])
    if cmd == "state":
        from inertia_forge.commands import run_state
        return run_state(argv[1:])
    if cmd == "status":
        from inertia_forge.commands import run_status
        return run_status(argv[1:])

    # Delegate session lifecycle (start / record-phase / close) to the bridge
    # CLI — the single sanctioned entry point.
    from inertia_forge.skill_bridge import main as bridge_main
    return bridge_main(argv)


if __name__ == "__main__":
    sys.exit(main())
