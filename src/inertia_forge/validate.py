"""`inertia-forge skills validate` — catch malformed skill definitions.

A typo in skill_definitions.yaml (gate on a non-existent step, an unknown
evidence_mode, a bad gate type) silently weakens enforcement. This validates
the active registry deterministically and reports every problem.
"""
from __future__ import annotations

from inertia_forge.evidence_collectors import _KNOWN_EVIDENCE_MODES

_GATE_TYPES = {"blocking", "checkpoint", "advisory"}


def validate_registry() -> list[str]:
    """Return a list of human-readable problems (empty == all valid)."""
    from inertia_forge.skill_registry import get_all_skills

    issues: list[str] = []
    for name, skill in sorted(get_all_skills().items()):
        steps = set(skill.steps)
        if not skill.steps:
            issues.append(f"{name}: has no steps")
        if skill.evidence_mode not in _KNOWN_EVIDENCE_MODES:
            issues.append(
                f"{name}: unknown evidence_mode {skill.evidence_mode!r} "
                f"(valid: {', '.join(_KNOWN_EVIDENCE_MODES)})",
            )
        for step, gate in skill.gates.items():
            if step not in steps:
                issues.append(f"{name}: gate on unknown step {step!r}")
            if gate not in _GATE_TYPES:
                issues.append(
                    f"{name}: gate {step!r} has invalid type {gate!r} "
                    f"(valid: {', '.join(sorted(_GATE_TYPES))})",
                )
        for phase, mode in skill.phase_evidence.items():
            if phase not in steps:
                issues.append(f"{name}: phase_evidence on unknown step {phase!r}")
            if mode not in _KNOWN_EVIDENCE_MODES:
                issues.append(f"{name}: phase_evidence {phase!r} unknown mode {mode!r}")
        if skill.loop_max < 0:
            issues.append(f"{name}: loop_max must be >= 0 (got {skill.loop_max})")
    return issues


def run_validate() -> int:
    issues = validate_registry()
    if not issues:
        from inertia_forge.skill_registry import get_all_skills
        print(f"OK: {len(get_all_skills())} skills valid.")
        return 0
    print(f"{len(issues)} problem(s) in the skill registry:")
    for i in issues:
        print(f"  - {i}")
    return 1
