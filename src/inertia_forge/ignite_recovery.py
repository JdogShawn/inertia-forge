"""Circuit-breaker recovery guidance.

When the ignite loop trips its breaker, name the dominant failure mode and point
at the next concrete action — so a human (or the next run) knows *why* it stopped
and what to do, instead of just "circuit breaker tripped". Deterministic: a tally
over the recorded failure reasons.
"""
from __future__ import annotations

_CAUSE = {
    "no_meaningful_output": "tasks produced no meaningful output repeatedly — "
                            "check the dispatch prompt and verification commands",
    "agent_failed": "the agent dispatch failed repeatedly — check the agent CLI, "
                    "model, and token budget",
    "review_unresolved": "review findings went unresolved within the iteration cap "
                         "— raise --max-review-iterations or fix manually",
}
_RECOVERY = ("Recovery: address the cause above, then "
             "`inertia-forge ignite resume <run-id>` (or re-plan with "
             "`inertia-forge plan`)")


def recovery_guidance(failure_reasons: dict[str, str]) -> list[str]:
    """Human-readable guidance lines for a tripped breaker (cause + next step)."""
    if not failure_reasons:
        return [_RECOVERY]
    tally: dict[str, int] = {}
    for reason in failure_reasons.values():
        tally[reason] = tally.get(reason, 0) + 1
    dominant = max(tally, key=lambda r: tally[r])
    cause = _CAUSE.get(dominant, f"repeated failure: {dominant}")
    return [f"Cause: {cause}", _RECOVERY]
