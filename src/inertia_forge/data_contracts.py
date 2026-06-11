"""Cross-skill finding traceability and data contracts.

Tracks findings through their full lifecycle:
  open -> tasked -> fixed -> verified (or wontfix)

Bounded at max_findings to prevent unbounded growth.
"""
from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class FindingTrace:
    """Full traceability for one finding through its lifecycle."""

    finding_id: str
    severity: str  # P0/P1/P2
    description: str
    source_skill: str
    source_step: str
    task_id: str | None = None
    fix_commit: str | None = None
    verified_in: str | None = None
    status: str = "open"  # open/tasked/fixed/verified/wontfix


class FindingTracker:
    """Tracks findings across skills and steps with deduplication."""

    def __init__(self, max_findings: int = 500) -> None:
        self._findings: dict[str, FindingTrace] = {}
        self._counter = 0
        self._max = max_findings

    def register(
        self,
        severity: str,
        description: str,
        source_skill: str,
        source_step: str,
    ) -> str:
        """Register a finding. Returns finding_id (empty if bounded)."""
        if len(self._findings) >= self._max:
            return ""
        self._counter += 1
        fid = f"F-{self._counter:04d}"
        self._findings[fid] = FindingTrace(
            finding_id=fid,
            severity=severity,
            description=description,
            source_skill=source_skill,
            source_step=source_step,
        )
        return fid

    def link_task(self, finding_id: str, task_id: str) -> bool:
        """Link finding to its fix task."""
        f = self._findings.get(finding_id)
        if not f:
            return False
        self._findings[finding_id] = replace(
            f, task_id=task_id, status="tasked"
        )
        return True

    def link_fix(self, finding_id: str, commit: str) -> bool:
        """Link finding to the commit that fixes it."""
        f = self._findings.get(finding_id)
        if not f:
            return False
        self._findings[finding_id] = replace(
            f, fix_commit=commit, status="fixed"
        )
        return True

    def verify(self, finding_id: str, verification_scope: str) -> bool:
        """Mark a finding as verified in a given scope."""
        f = self._findings.get(finding_id)
        if not f:
            return False
        self._findings[finding_id] = replace(
            f, verified_in=verification_scope, status="verified"
        )
        return True

    def get_unresolved_p0_p1(self) -> list[FindingTrace]:
        """Return all P0/P1 findings not yet verified or wontfix."""
        return [
            f
            for f in self._findings.values()
            if f.severity in ("P0", "P1")
            and f.status not in ("verified", "wontfix")
        ]

    def get_trace(self, finding_id: str) -> FindingTrace | None:
        """Look up a finding by ID."""
        return self._findings.get(finding_id)

    def all_p0_p1_resolved(self) -> bool:
        """True when no P0/P1 findings are unresolved."""
        return len(self.get_unresolved_p0_p1()) == 0
