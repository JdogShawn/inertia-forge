"""inertia-forge command-line interface.

  inertia-forge init [--target DIR]   install Claude Code hooks into a project
  inertia-forge skills [validate]      list / validate the skill registry
  inertia-forge start <skill> <target> start a forge session
  inertia-forge record-phase <p> <t>   record a phase (auto-closes on all-green)
  inertia-forge status                 forge session + plan/tasks + last/next
  inertia-forge close                  close (refuses while gates remain)
  inertia-forge arch <path>            deterministic architecture check
  inertia-forge verify [dir] [--cov P] run pytest + report pass/fail/coverage
  inertia-forge check [path] [--tests] project gate: arch + secrets (+ tests)
  inertia-forge task ...               manage the native task store
  inertia-forge state [--done/--next]  session-continuity ledger
  inertia-forge log [--claims]         view the audit trail
  inertia-forge pack                   bundle context to .forge/context_pack.md
  inertia-forge read <skill>           mark a skill's methodology doc as read
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


# command -> (module, function). Lazy-imported so the CLI stays fast.
_DISPATCH = {
    "init": ("inertia_forge.init", "run_init"),
    "task": ("inertia_forge.task_cli", "run_task"),
    "arch": ("inertia_forge.commands", "run_arch"),
    "verify": ("inertia_forge.commands", "run_verify"),
    "check": ("inertia_forge.commands", "run_check"),
    "state": ("inertia_forge.commands", "run_state"),
    "status": ("inertia_forge.commands", "run_status"),
    "log": ("inertia_forge.commands", "run_log"),
    "read": ("inertia_forge.commands", "run_read"),
    "pack": ("inertia_forge.commands", "run_pack"),
    "scan-deps": ("inertia_forge.commands", "run_scan_deps"),
    "doctor": ("inertia_forge.doctor", "run_doctor"),
    "sweep": ("inertia_forge.sweep", "run_sweep"),
}


def _run_skills(argv: list[str]) -> int:
    if len(argv) > 1 and argv[1] == "validate":
        from inertia_forge.validate import run_validate
        return run_validate()
    if len(argv) > 1 and argv[1] == "export":
        from inertia_forge.export import run_export
        return run_export(argv[2:])
    return _list_skills()


def main(argv: list[str] | None = None) -> int:
    import importlib

    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else ""

    if cmd in ("skills", "list"):
        return _run_skills(argv)
    if cmd in _DISPATCH:
        mod, fn = _DISPATCH[cmd]
        return getattr(importlib.import_module(mod), fn)(argv[1:])

    # Delegate session lifecycle (start / record-phase / close) to the bridge.
    from inertia_forge.skill_bridge import main as bridge_main
    return bridge_main(argv)


if __name__ == "__main__":
    sys.exit(main())
