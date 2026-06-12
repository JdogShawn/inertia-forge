"""Ignite run-state — persist a paused autonomous run so it resumes across
separate CLI invocations.

A run pauses when it reaches a human-gated task (a task whose ``requires`` is
``"human"``). The state is written to ``.forge/ignite/runs/<run-id>.state.json``
with the tasks already completed, so ``ignite resume <run-id>`` picks up exactly
where it stopped. Pure JSON I/O — deterministic, inspectable, git-diffable.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

_RUN_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_MAX_STATE_BYTES = 1 * 1024 * 1024  # reject corrupt/hostile oversized state


@dataclass
class RunState:
    """Serializable state for a paused ignite run."""

    run_id: str
    plan_id: str = ""
    completed_tasks: list[str] = field(default_factory=list)
    paused_task_id: str = ""
    max_parallel: int = 3
    created_at: str = ""
    paused_at: str = ""

    def __post_init__(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.paused_at:
            self.paused_at = now


def _runs_dir(project_root: Path) -> Path:
    return project_root / ".forge" / "ignite" / "runs"


def _validate_run_id(run_id: str) -> None:
    if not run_id or not _RUN_ID_RE.match(run_id) or run_id in (".", ".."):
        raise ValueError(
            f"invalid run id {run_id!r} — only A-Z a-z 0-9 . _ - allowed",
        )


def save_run_state(project_root: Path, state: RunState) -> Path:
    """Persist run state to JSON; returns the file path."""
    _validate_run_id(state.run_id)
    out_dir = _runs_dir(project_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{state.run_id}.state.json"
    path.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")
    return path


def load_run_state(project_root: Path, run_id: str) -> RunState:
    """Load run state; raises FileNotFoundError if missing, ValueError if unsafe."""
    _validate_run_id(run_id)
    runs_dir = _runs_dir(project_root)
    path = (runs_dir / f"{run_id}.state.json").resolve()
    if not str(path).startswith(str(runs_dir.resolve())):
        raise ValueError(f"run id resolves outside runs dir: {run_id!r}")
    if not path.exists():
        raise FileNotFoundError(f"run state not found: {path}")
    if path.stat().st_size > _MAX_STATE_BYTES:
        raise ValueError(f"run state file too large ({path.stat().st_size} bytes)")
    return RunState(**json.loads(path.read_text(encoding="utf-8")))


def save_pause_state(
    project_root: Path, plan_id: str, completed_tasks: list[str],
    paused_task_id: str, max_parallel: int = 3,
) -> str:
    """Create + save a pause state, returning the generated run_id."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    run_id = f"ignite-{ts}-{os.urandom(3).hex()}"
    save_run_state(project_root, RunState(
        run_id=run_id, plan_id=plan_id,
        completed_tasks=list(completed_tasks),
        paused_task_id=paused_task_id, max_parallel=max_parallel,
    ))
    return run_id


def list_runs(project_root: Path) -> list[str]:
    """Run ids of all persisted (paused) runs, newest first."""
    runs_dir = _runs_dir(project_root)
    if not runs_dir.exists():
        return []
    ids = [p.name[: -len(".state.json")] for p in runs_dir.glob("*.state.json")]
    return sorted(ids, reverse=True)
