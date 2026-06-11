"""真実の眼 Eye of Truth — Auto-Severity System.

Computes severity for measurable findings deterministically.
Measurable findings have LOCKED severity — AI cannot override,
defer, or relabel. Only human approval via forge-override CLI.
"""
from __future__ import annotations

from dataclasses import dataclass


class SeverityLockError(Exception):
    """Raised when attempting to override a measurable finding's severity."""


# ── Finding Types ──────────────────────────────────────────


@dataclass(frozen=True)
class MeasurableFinding:
    """Finding with COMPUTED severity that CANNOT be overridden by AI."""

    finding_id: str
    category: str
    evidence_command: str
    evidence_output: str
    computed_severity: str
    description: str

    def override_severity(self, new_severity: str) -> None:
        raise SeverityLockError(
            f"Override denied for {self.finding_id}. "
            f"Measurable finding severity is LOCKED. "
            f"Human approval required. "
            f"Run: forge-override {self.finding_id} "
            f"--severity {new_severity} --reason '...'"
        )

    def defer(self) -> None:
        raise SeverityLockError(
            f"Defer denied for {self.finding_id}. "
            f"Measurable findings cannot be deferred."
        )

    def relabel(self, new_severity: str) -> None:
        raise SeverityLockError(
            f"Relabel denied for {self.finding_id}. "
            f"Measurable findings cannot be relabeled."
        )


@dataclass
class SubjectiveFinding:
    """Finding with AI-assigned severity that CAN be adjusted."""

    finding_id: str
    category: str
    description: str
    assigned_severity: str
    evidence: str


# ── Severity Rules ─────────────────────────────────────────

SEVERITY_RULES: dict[str, str] = {
    "wiring_fail": "P0",
    "test_fail": "P0",
    "test_error": "P0",
    "coverage_below_80": "P0",
    "coverage_below_90": "P1",
    "arch_violation": "P1",
    "pragma_gaming": "P1",
    "finding_discrepancy": "P0",
    "oversized_file": "P2",
}


# ── Classifier ─────────────────────────────────────────────


_MEASURABLE_SOURCES = frozenset({
    "wiring", "test", "architecture", "coverage", "discrepancy",
})


class AutoSeverity:
    """Computes severity for measurable findings. AI cannot override."""

    def classify(
        self, source: str, evidence: dict,
    ) -> MeasurableFinding | SubjectiveFinding:
        """Determine measurable vs subjective and compute/assign severity."""
        if source in _MEASURABLE_SOURCES:
            severity = self._compute_severity(source, evidence)
            return MeasurableFinding(
                finding_id=evidence.get("finding_id", ""),
                category=source,
                evidence_command=evidence.get("command", ""),
                evidence_output=evidence.get("output", ""),
                computed_severity=severity,
                description=evidence.get("description", ""),
            )
        return SubjectiveFinding(
            finding_id=evidence.get("finding_id", ""),
            category=source,
            description=evidence.get("description", ""),
            assigned_severity=evidence.get("severity", "P2"),
            evidence=evidence.get("evidence", ""),
        )

    def _compute_severity(self, source: str, evidence: dict) -> str:
        """Compute severity from rules. Deterministic, no AI."""
        if source == "wiring" and not evidence.get("passed", False):
            return SEVERITY_RULES["wiring_fail"]
        if source == "test":
            return self._compute_test_severity(evidence)
        if source == "coverage":
            return self._compute_coverage_severity(evidence)
        if source == "architecture":
            return self._compute_arch_severity(evidence)
        if source == "discrepancy":
            return SEVERITY_RULES["finding_discrepancy"]
        return "P2"

    def _compute_test_severity(self, evidence: dict) -> str:
        if evidence.get("errors", 0) > 0:
            return SEVERITY_RULES["test_error"]
        if evidence.get("failed", 0) > 0:
            return SEVERITY_RULES["test_fail"]
        return "P2"

    def _compute_coverage_severity(self, evidence: dict) -> str:
        cov = evidence.get("coverage", 0)
        if cov < 0.80:
            return SEVERITY_RULES["coverage_below_80"]
        if cov < 0.90:
            return SEVERITY_RULES["coverage_below_90"]
        return "P2"

    def _compute_arch_severity(self, evidence: dict) -> str:
        if not evidence.get("passed", True):
            return SEVERITY_RULES["arch_violation"]
        if evidence.get("pragma_flagged", False):
            return SEVERITY_RULES["pragma_gaming"]
        if evidence.get("oversized", False):
            return SEVERITY_RULES["oversized_file"]
        return "P2"
