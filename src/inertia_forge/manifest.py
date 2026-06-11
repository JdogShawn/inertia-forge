"""神之眼 Eyes of God — Forge Manifest System.

Dynamic, scoped, exit-criteria-rich manifest that records everything
the forge does with SHA-256 evidence hashes. Immutable once written.

The manifest GROWS as work generates sub-steps. Not pre-defined.
Scopes nest hierarchically. Exit criteria record actual values.
"""
from __future__ import annotations

import hashlib
import json
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


# ── Data Models (all frozen) ─────────────────────────────────

_MAX_SCOPES = 50
_MAX_STEPS_PER_SCOPE = 200


@dataclass(frozen=True)
class ExitCriteria:
    """What MUST be true for a step to pass."""

    description: str
    metric_name: str
    required_value: str
    actual_value: str
    passed: bool


@dataclass(frozen=True)
class StepRecord:
    """One completed sub-step with full evidence."""

    step_name: str
    scope: str
    started_at: str
    completed_at: str
    exit_criteria: tuple[ExitCriteria, ...]
    all_criteria_passed: bool
    evidence_hash: str
    evidence_summary: str


# ── Manifest ─────────────────────────────────────────────────


class ForgeManifest:
    """Living document that grows as work generates sub-steps."""

    def __init__(self, organism_name: str, revision: int = 1) -> None:
        self.organism_name = organism_name
        self.revision = revision
        self._scopes: OrderedDict[str, _ScopeData] = OrderedDict()
        self._created_at = _now()

    # -- Scope management ------------------------------------------

    def register_scope(self, name: str, parent: str | None = None) -> None:
        """Create a new scope. Bounded at _MAX_SCOPES."""
        if len(self._scopes) >= _MAX_SCOPES:
            return
        self._scopes[name] = _ScopeData(parent=parent)

    def get_scope_names(self) -> list[str]:
        """All registered scope names."""
        return list(self._scopes.keys())

    # -- Step management -------------------------------------------

    def register_step(self, scope: str, step_name: str) -> None:
        """Register a step within a scope. Manifest GROWS."""
        sd = self._scopes.get(scope)
        if sd is None:
            return
        if len(sd.registered) >= _MAX_STEPS_PER_SCOPE:
            return
        sd.registered.add(step_name)

    def get_registered_steps(self, scope: str) -> list[str]:
        """Steps registered in a scope."""
        sd = self._scopes.get(scope)
        if sd is None:
            return []
        return sorted(sd.registered)

    # -- Recording -------------------------------------------------

    def record_step(
        self,
        scope: str,
        step_name: str,
        exit_criteria: list[ExitCriteria],
        evidence: dict[str, Any],
    ) -> StepRecord:
        """Record a completed step with exit criteria and evidence."""
        sd = self._scopes.get(scope)
        if sd is None:
            raise ValueError(f"Unknown scope: {scope}")
        if len(sd.records) >= _MAX_STEPS_PER_SCOPE:
            return sd.records[-1]  # silently cap — bounded collection

        criteria_tuple = tuple(exit_criteria)
        all_passed = all(ec.passed for ec in criteria_tuple)
        ev_hash = _hash_evidence(evidence)
        summary = _summarize_criteria(criteria_tuple)
        now = _now()

        record = StepRecord(
            step_name=step_name,
            scope=scope,
            started_at=now,
            completed_at=now,
            exit_criteria=criteria_tuple,
            all_criteria_passed=all_passed,
            evidence_hash=ev_hash,
            evidence_summary=summary,
        )
        sd.records.append(record)
        return record

    # -- Queries ---------------------------------------------------

    def can_proceed_scope(self, scope: str) -> tuple[bool, str]:
        """Can we proceed? Checks ALL recorded steps in scope passed."""
        sd = self._scopes.get(scope)
        if sd is None:
            return (False, f"Unknown scope: {scope}")
        for rec in sd.records:
            if not rec.all_criteria_passed:
                return (False, f"Step '{rec.step_name}' in scope '{scope}' has failed criteria")
        return (True, "")

    def total_steps_recorded(self) -> int:
        """Total steps across ALL scopes."""
        return sum(len(sd.records) for sd in self._scopes.values())

    def get_failures(self) -> list[tuple[str, str, ExitCriteria]]:
        """All failed criteria: (scope, step, criteria)."""
        failures: list[tuple[str, str, ExitCriteria]] = []
        for scope_name, sd in self._scopes.items():
            for rec in sd.records:
                for ec in rec.exit_criteria:
                    if not ec.passed:
                        failures.append((scope_name, rec.step_name, ec))
        return failures

    # -- Persistence -----------------------------------------------

    def save(self, path: str) -> None:
        """Serialize manifest to JSON file."""
        from inertia_forge._serialization import record_to_dict

        data = {
            "organism_name": self.organism_name,
            "revision": self.revision,
            "created_at": self._created_at,
            "scopes": {},
        }
        for name, sd in self._scopes.items():
            data["scopes"][name] = {
                "parent": sd.parent,
                "records": [record_to_dict(r) for r in sd.records],
                "registered": sorted(sd.registered),
            }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: str) -> ForgeManifest:
        """Deserialize manifest from file."""
        from inertia_forge._serialization import dict_to_record

        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        m = cls(data["organism_name"], data.get("revision", 1))
        m._created_at = data.get("created_at", _now())
        for name, sd_data in data.get("scopes", {}).items():
            m._scopes[name] = _ScopeData(parent=sd_data.get("parent"))
            m._scopes[name].registered = set(sd_data.get("registered", []))
            for rd in sd_data.get("records", []):
                m._scopes[name].records.append(dict_to_record(rd))
        return m


# ── Internal ─────────────────────────────────────────────────


class _ScopeData:
    """Mutable internal storage for a scope."""

    __slots__ = ("parent", "registered", "records")

    def __init__(self, parent: str | None = None) -> None:
        self.parent = parent
        self.registered: set[str] = set()
        self.records: list[StepRecord] = []


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_evidence(evidence: dict[str, Any]) -> str:
    raw = json.dumps(evidence, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _summarize_criteria(criteria: tuple[ExitCriteria, ...]) -> str:
    passed = sum(1 for c in criteria if c.passed)
    total = len(criteria)
    return f"{passed}/{total} criteria passed"
