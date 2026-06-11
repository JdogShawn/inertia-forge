"""PairCoder-aware forge evidence — gates backed by real task management.

Bundle F: pc-plan and start-task are workflow skills whose "completion" is
defined by bpsai-pair state, not by code metrics or a SHA stamp. Each gated
phase verifies that state on disk (via paircoder_state) and emits P0 findings
when the expected artifact is missing or malformed — which (via
completion_lock's p0 check) keeps the blocking gate open until the real work
exists:

  pc_plan.budget_check  -> every task carries a complexity estimate (budgeted)
  pc_plan.create_plan   -> a plan exists AND its type is valid (not maintenance)
  pc_plan.add_tasks     -> >=1 task file AND every task id is T<sprint>.<seq>
  start_task.preflight  -> active task set AND its status == in_progress
  start_task.complete   -> active task AC all checked AND status == done

The evidence hash is a deterministic stamp — the FINDINGS carry the
verification result; the hash only proves the phase ran.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from inertia_forge.paircoder import cli, state as st


def _stamp(skill: str, phase: str, target: str) -> str:
    """Deterministic SHA-256 over the canonical tuple (never a bypass prefix)."""
    ts = datetime.now(timezone.utc).isoformat()
    return hashlib.sha256(
        f"{skill}|{phase}|{target}|{ts}|task_management".encode()
    ).hexdigest()


def _p0(rule: str, message: str) -> dict:
    return {
        "severity": "P0", "rule": rule,
        "file": "<paircoder>", "line": 0, "message": message,
    }


# -- pc_plan verifiers -------------------------------------------------


def _verify_budget_check() -> list[dict]:
    tasks = st.task_files()
    if not tasks:
        return [_p0(
            "budget_not_estimated",
            "budget_check: no tasks to budget — add complexity-estimated "
            "tasks (bpsai-pair budget check) before sealing",
        )]
    values = {t.name: st.complexity_value(t) for t in tasks}
    missing = [n for n, v in values.items() if v is None]
    out_of_range = [n for n, v in values.items() if v is not None and not 0 <= v <= 100]
    findings: list[dict] = []
    if missing:
        findings.append(_p0(
            "budget_not_estimated",
            f"budget_check: {len(missing)} task(s) lack a complexity "
            f"estimate: {', '.join(missing[:5])}",
        ))
    if out_of_range:
        findings.append(_p0(
            "complexity_out_of_range",
            f"budget_check: {len(out_of_range)} task(s) have complexity "
            f"outside 0-100: {', '.join(out_of_range[:5])}",
        ))
    return findings


def _verify_create_plan() -> list[dict]:
    plans = st.plan_files()
    if not plans:
        return [_p0(
            "no_plan",
            "create_plan: no plan in .paircoder/plans/ — create one "
            "(bpsai-pair plan) before sealing this phase",
        )]
    bad = [
        f"{p.name}:{st.plan_type(p)}"
        for p in plans
        if st.plan_type(p) not in st.VALID_PLAN_TYPES
    ]
    if bad:
        return [_p0(
            "invalid_plan_type",
            f"create_plan: plan type must be one of {st.VALID_PLAN_TYPES} "
            f"(NOT maintenance); offending: {', '.join(bad)}",
        )]
    return []


def _verify_add_tasks() -> list[dict]:
    tasks = st.task_files()
    if not tasks:
        return [_p0(
            "no_tasks",
            "add_tasks: .paircoder/tasks/ has 0 task files — add tasks to "
            "the plan before sealing this phase",
        )]
    texts = {t: st.read(t) or "" for t in tasks}
    bad = [
        tid for t in tasks
        if (tid := st.task_id(t)) and not st.task_id_valid(tid)
    ]
    no_ac = [t.name for t in tasks if st.ac_total(texts[t]) == 0]
    no_ver = [t.name for t in tasks if not st.has_verification(texts[t])]
    findings: list[dict] = []
    if bad:
        findings.append(_p0(
            "bad_task_id",
            f"add_tasks: task IDs must match T<sprint>.<seq> (e.g. T1.1); "
            f"offending: {', '.join(bad[:5])}",
        ))
    if no_ac:
        findings.append(_p0(
            "no_acceptance_criteria",
            f"add_tasks: {len(no_ac)} task(s) have no acceptance criteria "
            f"(checkbox items) — tasks without AC must not be started: "
            f"{', '.join(no_ac[:5])}",
        ))
    if no_ver:
        findings.append(_p0(
            "no_verification",
            f"add_tasks: {len(no_ver)} task(s) lack a # Verification section "
            f"(test command) — TDD requires it: {', '.join(no_ver[:5])}",
        ))
    return findings


def _verify_cli_sync() -> list[dict]:
    """Sanctioned-CLI gate: tasks must be managed through bpsai-pair, not
    hand-edited (no 'changed outside CLI' drift)."""
    drifted = cli.drifted_tasks()
    if drifted:
        return [_p0(
            "cli_drift",
            f"cli_sync: {len(drifted)} task(s) changed outside the sanctioned "
            f"CLI — run `bpsai-pair task update <id> --resync`: "
            f"{', '.join(drifted[:5])}",
        )]
    return []


# -- start_task verifiers ----------------------------------------------


def _verify_preflight() -> list[dict]:
    tid = st.active_task_id()
    if tid is None:
        return [_p0(
            "no_active_task",
            "preflight: no active task — run `bpsai-pair task update <id> "
            "--status in_progress` first",
        )]
    text = st.read_active_task()
    if text is None:
        return [_p0("task_file_missing", f"preflight: task file for {tid} not found")]
    if st.status_of(text) != "in_progress":
        return [_p0(
            "task_not_in_progress",
            f"preflight: active task {tid} status is "
            f"{st.status_of(text)!r}, expected 'in_progress'",
        )]
    return []


def _verify_complete() -> list[dict]:
    tid = st.active_task_id()
    if tid is None:
        return [_p0("no_active_task", "complete: no active task to complete")]
    text = st.read_active_task()
    if text is None:
        return [_p0("task_file_missing", f"complete: task file for {tid} not found")]
    findings: list[dict] = []
    unchecked = st.unchecked_ac(text)
    if unchecked > 0:
        findings.append(_p0(
            "ac_unmet",
            f"complete: {tid} has {unchecked} unchecked acceptance "
            f"criteria — meet them before closing",
        ))
    if st.status_of(text) != "done":
        findings.append(_p0(
            "task_not_done",
            f"complete: {tid} status is {st.status_of(text)!r}, expected 'done'",
        ))
    return findings


_VERIFIERS = {
    ("pc_plan", "budget_check"): _verify_budget_check,
    ("pc_plan", "create_plan"): _verify_create_plan,
    ("pc_plan", "add_tasks"): _verify_add_tasks,
    ("pc_plan", "cli_sync"): _verify_cli_sync,
    ("start_task", "preflight"): _verify_preflight,
    ("start_task", "complete"): _verify_complete,
    # planning-with-pm (provider-agnostic) — same task-management gates.
    ("planning_with_pm", "budget_check"): _verify_budget_check,
    ("planning_with_pm", "create_plan"): _verify_create_plan,
    ("planning_with_pm", "create_task_files"): _verify_add_tasks,
    # planning-with-trello — gate task creation on real artifacts.
    ("planning_with_trello", "create_tasks"): _verify_add_tasks,
    # designing-and-implementing — gate the planning phase (per-phase mode).
    ("designing_and_implementing", "plan_tasks"): _verify_add_tasks,
}


def collect_paircoder(
    skill: str, phase: str, target: str, analysis_dir: Path,
) -> tuple[list[dict], str]:
    """task_management mode — verify real PairCoder state for this phase.

    Ungated phases (not in _VERIFIERS) record cleanly with a stamp; the
    gated ones emit P0 findings when their PairCoder artifact is missing.
    """
    verifier = _VERIFIERS.get((skill, phase))
    findings = verifier() if verifier else []
    return findings, _stamp(skill, phase, target)
