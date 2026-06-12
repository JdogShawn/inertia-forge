"""死神の鎌 Death Scythe Step Validator — Prison Realm enforcement.

Blocks progression through forge steps unless previous steps have
evidence of completion recorded in the manifest. No skipping allowed.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from inertia_forge.manifest import ForgeManifest

if TYPE_CHECKING:
    from inertia_forge.data_contracts import FindingTracker

# ── Step Constants ──────────────────────────────────────────

BIRTH = "birth"
MIDAS_HAND = "midas_hand"
EXECUTE = "execute"
SPOTLIGHT = "spotlight"
RE_FORGE = "re_forge"
LIFE_VERIFY = "life_verify"
HEAVENS_GATE = "heavens_gate"
PURGE = "purge"
CERTIFICATION = "certification"
EVOLUTION = "evolution"

# Ordered list of all steps (determines progression order)
ALL_STEPS: tuple[str, ...] = (
    BIRTH, MIDAS_HAND, EXECUTE, SPOTLIGHT, RE_FORGE,
    LIFE_VERIFY, HEAVENS_GATE, PURGE, CERTIFICATION, EVOLUTION,
)

# Prerequisites: step -> list of required prior steps
STEP_PREREQUISITES: dict[str, list[str]] = {
    BIRTH: [],
    MIDAS_HAND: [BIRTH],
    EXECUTE: [MIDAS_HAND],
    SPOTLIGHT: [EXECUTE],
    RE_FORGE: [SPOTLIGHT],
    LIFE_VERIFY: [RE_FORGE],
    HEAVENS_GATE: [LIFE_VERIFY],
    PURGE: [HEAVENS_GATE],
    CERTIFICATION: [PURGE],
    EVOLUTION: [CERTIFICATION],
}

_SCOPE = "forge"


# ── Validator ───────────────────────────────────────────────


class ForgeStepValidator:
    """Enforces Death Scythe step ordering via manifest evidence."""

    def __init__(
        self,
        manifest: ForgeManifest,
        finding_tracker: FindingTracker | None = None,
    ) -> None:
        self._manifest = manifest
        self._finding_tracker = finding_tracker

    def validate_can_start(self, step_name: str) -> tuple[bool, str]:
        """Check whether a step can begin.

        Returns (allowed, reason). Checks that every prerequisite
        step has a passing record in the manifest.
        """
        if step_name not in STEP_PREREQUISITES:
            return (False, f"Unknown step: {step_name!r}")

        prerequisites = STEP_PREREQUISITES[step_name]
        if not prerequisites:
            return (True, "")

        passed_steps = self._get_passed_steps()
        for prereq in prerequisites:
            if prereq not in passed_steps:
                return (False, f"Prerequisite '{prereq}' has not passed")

        # Check unresolved P0/P1 from finding tracker
        if self._finding_tracker is not None:
            unresolved = self._finding_tracker.get_unresolved_p0_p1()
            if unresolved:
                ids = ", ".join(f.finding_id for f in unresolved)
                return (
                    False,
                    f"{len(unresolved)} unresolved P0/P1: {ids}",
                )

        return (True, "")

    def get_current_step(self) -> str:
        """Return the first incomplete step in the sequence."""
        passed = self._get_passed_steps()
        for step in ALL_STEPS:
            if step not in passed:
                return step
        return EVOLUTION  # all done — return last step

    def get_blocked_reason(self) -> str | None:
        """Why the current step is blocked, or None if not blocked."""
        current = self.get_current_step()
        allowed, reason = self.validate_can_start(current)
        if allowed:
            return None
        return reason

    def get_progress(self) -> dict[str, object]:
        """Return progress summary.

        Keys: completed (int), total (int), current (str), blocked (bool).
        """
        passed = self._get_passed_steps()
        current = self.get_current_step()
        allowed, _ = self.validate_can_start(current)
        return {
            "completed": len(passed),
            "total": len(ALL_STEPS),
            "current": current,
            "blocked": not allowed,
        }

    # ── Internal ────────────────────────────────────────────

    def _get_passed_steps(self) -> set[str]:
        """Collect step names with all_criteria_passed from manifest."""
        passed: set[str] = set()
        scope_data = self._manifest._scopes.get(_SCOPE)
        if scope_data is None:
            return passed
        for record in scope_data.records:
            if record.all_criteria_passed:
                passed.add(record.step_name)
        return passed
