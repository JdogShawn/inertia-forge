"""Engage — the autonomous task-execution loop.

Walks the task graph wave by wave (each :func:`taskgraph.parallel_waves` level is
a phase). For every pending task: skip it if its acceptance criteria are already
satisfied, otherwise dispatch it (to an agent, or to an injected runner), commit
the result, verify the commit carried meaningful output, and mark it done. A
circuit breaker stops the run when the failure ratio crosses a threshold; a
human-gated task pauses the run to resumable state.

The deterministic core never needs an LLM: ``--dry-run`` (or any injected
``task_runner``) drives the entire loop with zero model calls.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from inertia_forge.engage_commit import commit_task
from inertia_forge.engage_predispatch import CheckResult, pre_dispatch_check
from inertia_forge.engage_runstate import save_pause_state
from inertia_forge.engage_steps import (
    agent_task_runner,
    mark_task_done,
    now_iso,
    record_outcome,
    verify_output,
)


@dataclass
class EngageConfig:
    """How an engage run behaves."""

    project_root: Path = field(default_factory=lambda: Path("."))
    agent: str = "claude"
    model: str | None = None
    permission_mode: str = "auto"
    token_budget: int | None = None
    max_parallel: int = 1
    circuit_breaker_threshold: float = 0.5
    dry_run: bool = False
    commit: bool = True
    test_instruction: str = ""


@dataclass
class EngageResult:
    """Aggregate outcome of an engage run."""

    completed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    paused_task: str | None = None
    run_id: str | None = None
    phases_completed: int = 0
    circuit_breaker_triggered: bool = False
    failure_reasons: dict[str, str] = field(default_factory=dict)


class EngageRunner:
    """Executes the task graph wave-by-wave with a circuit breaker."""

    def __init__(self, config: EngageConfig | None = None, task_runner=None) -> None:
        self.config = config or EngageConfig()
        if task_runner is not None:
            self._runner = task_runner
        elif self.config.dry_run:
            self._runner = lambda task: True
            self.config.commit = False
        else:
            self._runner = lambda task: agent_task_runner(task, self.config)

    def run(self) -> EngageResult:
        from inertia_forge import taskgraph
        res = EngageResult()
        for wave in taskgraph.parallel_waves():
            pending = self._phase_pending(wave)
            if not pending:
                continue
            gated = self._first_gated(pending)
            if gated:
                res.paused_task = gated
                res.run_id = save_pause_state(
                    self.config.project_root, self._plan_id(),
                    res.completed, gated, self.config.max_parallel)
                break
            self._run_phase(pending, res)
            res.phases_completed += 1
            if self._check_breaker(res):
                res.circuit_breaker_triggered = True
                break
        return res

    def _run_phase(self, pending: list[str], res: EngageResult) -> None:
        if self.config.max_parallel > 1 and len(pending) > 1:
            from concurrent.futures import ThreadPoolExecutor
            workers = min(self.config.max_parallel, len(pending))
            with ThreadPoolExecutor(max_workers=workers) as pool:
                list(pool.map(lambda tid: self._run_task(tid, res), pending))
        else:
            for tid in pending:
                self._run_task(tid, res)

    def _run_task(self, tid: str, res: EngageResult) -> None:
        from inertia_forge import tasks
        task = tasks.get_task(tid)
        if task is None:
            return
        ac_texts = [c["text"] for c in task.get("acceptance_criteria", [])]
        if pre_dispatch_check(ac_texts, self.config.project_root) == CheckResult.ALREADY_SATISFIED:
            mark_task_done(tid)
            res.skipped.append(tid)
            res.completed.append(tid)
            record_outcome(task, "skipped", 0.0)
            return
        tasks.start_task(tid)
        start, t0 = now_iso(), time.monotonic()
        ok = self._runner(task)
        dur = time.monotonic() - t0
        if not ok:
            self._fail(tid, "agent_failed", task, dur, res)
            return
        if self.config.commit:
            commit_task(self.config.project_root, tid, task.get("title", ""), start)
            if not verify_output(self.config.project_root):
                self._fail(tid, "no_meaningful_output", task, dur, res)
                return
        mark_task_done(tid)
        res.completed.append(tid)
        record_outcome(task, "success", dur)

    def _fail(self, tid: str, why: str, task: dict, dur: float, res: EngageResult) -> None:
        res.failed.append(tid)
        res.failure_reasons[tid] = why
        record_outcome(task, "failed", dur)

    def _phase_pending(self, wave: list[str]) -> list[str]:
        from inertia_forge import tasks
        out = []
        for tid in wave:
            task = tasks.get_task(tid)
            if task and task.get("status") == "pending":
                out.append(tid)
        return out

    def _first_gated(self, pending: list[str]) -> str | None:
        from inertia_forge import tasks
        for tid in pending:
            task = tasks.get_task(tid)
            if task and task.get("requires") == "human":
                return tid
        return None

    def _plan_id(self) -> str:
        from inertia_forge import tasks
        plan = tasks.get_plan()
        return plan.get("id", "") if plan else ""

    def _check_breaker(self, res: EngageResult) -> bool:
        total = len(res.completed) + len(res.failed)
        if total == 0:
            return False
        return len(res.failed) / total >= self.config.circuit_breaker_threshold
