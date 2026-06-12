"""Native, dependency-free task management (INERTIA-style).

A self-contained plan/task store under ``.forge/forge_tasks.json`` — no external
CLI, no network. This backs the ``task_management`` evidence mode so a forge
session can gate on REAL plan/task/acceptance-criteria state that the forge
itself owns.

Store shape::

    {
      "plan":        {"id": "p1", "type": "feature", "title": "..."} | null,
      "active_task": "T1.1" | null,
      "tasks": {
        "T1.1": {
          "id": "T1.1", "title": "...", "status": "pending",
          "complexity": 5,
          "acceptance_criteria": [{"text": "...", "done": false}],
          "verification": "pytest tests/..."
        }
      }
    }

Everything is pure file/JSON I/O — deterministic, inspectable, git-diffable.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

STORE = Path(".forge") / "forge_tasks.json"
VALID_PLAN_TYPES = ("feature", "bugfix", "refactor", "chore")
VALID_STATUSES = ("pending", "in_progress", "done")
TASK_ID_RE = re.compile(r"^T\d+\.\d+$")


# ── Store I/O ────────────────────────────────────────────────────────
def _empty() -> dict:
    return {"plan": None, "active_task": None, "tasks": {}, "archived": {}}


def load() -> dict:
    """Load the store, or an empty store if absent/corrupt."""
    if not STORE.exists():
        return _empty()
    try:
        data = json.loads(STORE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _empty()
    data.setdefault("plan", None)
    data.setdefault("active_task", None)
    data.setdefault("tasks", {})
    data.setdefault("archived", {})
    return data


def save(data: dict) -> None:
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


# ── Plan ─────────────────────────────────────────────────────────────
def create_plan(plan_type: str, title: str, plan_id: str = "p1") -> dict:
    if plan_type not in VALID_PLAN_TYPES:
        raise ValueError(
            f"plan type must be one of {VALID_PLAN_TYPES} (got {plan_type!r})",
        )
    data = load()
    data["plan"] = {"id": plan_id, "type": plan_type, "title": title}
    save(data)
    return data["plan"]


# ── Tasks ────────────────────────────────────────────────────────────
def add_task(
    task_id: str, title: str, complexity: float,
    acceptance: list[str], verification: str,
    depends_on: list[str] | None = None,
) -> dict:
    if not TASK_ID_RE.match(task_id):
        raise ValueError(f"task id must match T<sprint>.<seq> (got {task_id!r})")
    if not acceptance:
        raise ValueError("a task needs at least one acceptance criterion")
    if not verification:
        raise ValueError("a task needs a verification (test) command — TDD")
    data = load()
    data["tasks"][task_id] = {
        "id": task_id, "title": title, "status": "pending",
        "complexity": float(complexity),
        "acceptance_criteria": [{"text": t, "done": False} for t in acceptance],
        "verification": verification,
        "depends_on": list(depends_on or []),
    }
    save(data)
    return data["tasks"][task_id]


def _require(data: dict, task_id: str) -> dict:
    task = data["tasks"].get(task_id)
    if task is None:
        raise ValueError(f"no such task: {task_id}")
    return task


def start_task(task_id: str) -> dict:
    data = load()
    task = _require(data, task_id)
    task["status"] = "in_progress"
    data["active_task"] = task_id
    save(data)
    return task


def check_ac(task_id: str, index: int) -> dict:
    data = load()
    task = _require(data, task_id)
    ac = task["acceptance_criteria"]
    if not 0 <= index < len(ac):
        raise ValueError(f"acceptance criterion {index} out of range")
    ac[index]["done"] = True
    save(data)
    return task


def complete_task(task_id: str) -> dict:
    data = load()
    task = _require(data, task_id)
    unchecked = [c for c in task["acceptance_criteria"] if not c["done"]]
    if unchecked:
        raise ValueError(
            f"cannot complete {task_id}: {len(unchecked)} unmet acceptance "
            "criteria — check them off first",
        )
    task["status"] = "done"
    task["completed_at"] = datetime.now(timezone.utc).isoformat()
    save(data)
    return task


def update_task(
    task_id: str, title: str | None = None,
    complexity: float | None = None, verification: str | None = None,
    depends_on: list[str] | None = None, scope: list[str] | None = None,
) -> dict:
    """Edit a task in place (title / complexity / verification / depends_on / scope)."""
    data = load()
    task = _require(data, task_id)
    if title is not None:
        task["title"] = title
    if complexity is not None:
        task["complexity"] = float(complexity)
    if verification is not None:
        task["verification"] = verification
    if depends_on is not None:
        task["depends_on"] = list(depends_on)
    if scope is not None:
        task["scope"] = list(scope)
    save(data)
    return task


def add_acceptance(task_id: str, text: str) -> dict:
    """Append a new (unchecked) acceptance criterion to a task."""
    data = load()
    task = _require(data, task_id)
    task["acceptance_criteria"].append({"text": text, "done": False})
    save(data)
    return task


# Lifecycle store ops (next/archive/restore/list_archived/cleanup_done) live in
# task_archive.py and are re-exported at the bottom of this module — split out to
# keep both files under the function-count ceiling.


# ── Reads ────────────────────────────────────────────────────────────
def get_plan() -> dict | None:
    return load().get("plan")


def get_task(task_id: str) -> dict | None:
    return load()["tasks"].get(task_id)


def list_tasks() -> list[dict]:
    return [load()["tasks"][k] for k in sorted(load()["tasks"])]


def active_task_id() -> str | None:
    return load().get("active_task")


# Re-export lifecycle store ops (defined in task_archive to respect the function
# ceiling). Imported at module bottom so the leaf module can lazily import us back.
from inertia_forge.task_archive import (  # noqa: E402
    archive_task,
    cleanup_done,
    list_archived,
    next_task,
    restore_task,
)
