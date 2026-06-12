"""Native task_management evidence — gates backed by the forge's own task store.

INERTIA-native task verifiers — they read the forge's OWN task store
(inertia_forge.tasks) with ZERO external dependencies, so `task_management`
mode is fully self-contained.

Verifiers are keyed by PHASE name (not skill), so any skill whose steps use the
standard names gets gated automatically:

  budget_check       -> every task carries a complexity estimate in 0..100
  create_plan        -> a plan exists AND its type is valid
  add_tasks          -> >=1 task, each with a valid id + AC + verification
  create_task_files  -> alias of add_tasks
  preflight          -> the active task is set AND status == in_progress
  complete           -> the active task's AC are all met AND status == done

A failed predicate yields a P0 finding, which (via completion_lock's p0 check)
keeps the blocking gate open until the real task state exists.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from inertia_forge import tasks as t


def _stamp(skill: str, phase: str, target: str) -> str:
    ts = datetime.now(timezone.utc).isoformat()
    return hashlib.sha256(
        f"{skill}|{phase}|{target}|{ts}|task_management".encode()
    ).hexdigest()


def _p0(rule: str, message: str) -> dict:
    return {"severity": "P0", "rule": rule, "file": "<tasks>", "line": 0, "message": message}


def _verify_budget() -> list[dict]:
    tasks = t.list_tasks()
    if not tasks:
        return [_p0("budget_not_estimated",
                    "budget_check: no tasks — add complexity-estimated tasks "
                    "(inertia-forge task add ... --complexity N) before sealing")]
    bad = [x["id"] for x in tasks if not 0 <= x.get("complexity", -1) <= 100]
    if bad:
        return [_p0("complexity_out_of_range",
                    f"budget_check: task(s) lack a 0-100 complexity: {', '.join(bad[:5])}")]
    return []


def _verify_plan() -> list[dict]:
    plan = t.get_plan()
    if not plan:
        return [_p0("no_plan",
                    "create_plan: no plan — run `inertia-forge task plan "
                    "--type feature --title ...` before sealing")]
    if plan.get("type") not in t.VALID_PLAN_TYPES:
        return [_p0("invalid_plan_type",
                    f"create_plan: plan type must be one of {t.VALID_PLAN_TYPES} "
                    f"(got {plan.get('type')!r})")]
    return []


def _verify_add_tasks() -> list[dict]:
    tasks = t.list_tasks()
    if not tasks:
        return [_p0("no_tasks",
                    "add_tasks: 0 tasks — add tasks to the plan before sealing")]
    findings: list[dict] = []
    bad_id = [x["id"] for x in tasks if not t.TASK_ID_RE.match(x.get("id", ""))]
    no_ac = [x["id"] for x in tasks if not x.get("acceptance_criteria")]
    no_ver = [x["id"] for x in tasks if not x.get("verification")]
    if bad_id:
        findings.append(_p0("bad_task_id",
                            f"add_tasks: ids must match T<sprint>.<seq>: {', '.join(bad_id[:5])}"))
    if no_ac:
        findings.append(_p0("no_acceptance_criteria",
                            f"add_tasks: task(s) with no acceptance criteria: {', '.join(no_ac[:5])}"))
    if no_ver:
        findings.append(_p0("no_verification",
                            f"add_tasks: task(s) lacking a verification command (TDD): {', '.join(no_ver[:5])}"))
    return findings


def _verify_preflight() -> list[dict]:
    tid = t.active_task_id()
    if tid is None:
        return [_p0("no_active_task",
                    "preflight: no active task — run `inertia-forge task start <id>` first")]
    task = t.get_task(tid)
    if task is None:
        return [_p0("task_missing", f"preflight: active task {tid} not found")]
    if task.get("status") != "in_progress":
        return [_p0("task_not_in_progress",
                    f"preflight: active task {tid} status is {task.get('status')!r}, "
                    "expected 'in_progress'")]
    return []


def _verify_complete() -> list[dict]:
    tid = t.active_task_id()
    if tid is None:
        return [_p0("no_active_task", "complete: no active task to complete")]
    task = t.get_task(tid)
    if task is None:
        return [_p0("task_missing", f"complete: active task {tid} not found")]
    findings: list[dict] = []
    unmet = [c for c in task.get("acceptance_criteria", []) if not c.get("done")]
    if unmet:
        findings.append(_p0("ac_unmet",
                            f"complete: {tid} has {len(unmet)} unmet acceptance criteria"))
    if task.get("status") != "done":
        findings.append(_p0("task_not_done",
                            f"complete: {tid} status is {task.get('status')!r}, expected 'done'"))
    return findings


_VERIFIERS = {
    "budget_check": _verify_budget,
    "create_plan": _verify_plan,
    "add_tasks": _verify_add_tasks,
    "create_task_files": _verify_add_tasks,
    "preflight": _verify_preflight,
    "complete": _verify_complete,
}


def collect_native_task(
    skill: str, phase: str, target: str, analysis_dir: Path,
) -> tuple[list[dict], str]:
    """task_management mode (native) — verify the forge's own task store.

    Ungated phases record cleanly with a stamp; gated phases emit P0 findings
    when their task artifact is missing or malformed.
    """
    verifier = _VERIFIERS.get(phase)
    findings = verifier() if verifier else []
    return findings, _stamp(skill, phase, target)
