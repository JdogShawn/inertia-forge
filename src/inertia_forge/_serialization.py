"""Serialization helpers for forge manifest — extracted spoke module."""
from __future__ import annotations

import json
from typing import Any

from inertia_forge.manifest import ExitCriteria, StepRecord


def record_to_dict(r: StepRecord) -> dict[str, Any]:
    """Convert StepRecord to serializable dict."""
    return {
        "step_name": r.step_name,
        "scope": r.scope,
        "started_at": r.started_at,
        "completed_at": r.completed_at,
        "exit_criteria": [
            {
                "description": ec.description,
                "metric_name": ec.metric_name,
                "required_value": ec.required_value,
                "actual_value": ec.actual_value,
                "passed": ec.passed,
            }
            for ec in r.exit_criteria
        ],
        "all_criteria_passed": r.all_criteria_passed,
        "evidence_hash": r.evidence_hash,
        "evidence_summary": r.evidence_summary,
    }


def dict_to_record(d: dict[str, Any]) -> StepRecord:
    """Convert dict back to StepRecord."""
    criteria = tuple(
        ExitCriteria(
            description=ec["description"],
            metric_name=ec["metric_name"],
            required_value=ec["required_value"],
            actual_value=ec["actual_value"],
            passed=ec["passed"],
        )
        for ec in d.get("exit_criteria", [])
    )
    return StepRecord(
        step_name=d["step_name"],
        scope=d["scope"],
        started_at=d["started_at"],
        completed_at=d["completed_at"],
        exit_criteria=criteria,
        all_criteria_passed=d["all_criteria_passed"],
        evidence_hash=d["evidence_hash"],
        evidence_summary=d["evidence_summary"],
    )


def serialize_manifest(data: dict[str, Any]) -> str:
    """Serialize manifest data to JSON string."""
    return json.dumps(data, indent=2, ensure_ascii=False)


def deserialize_manifest(text: str) -> dict[str, Any]:
    """Deserialize manifest from JSON string."""
    return json.loads(text)
