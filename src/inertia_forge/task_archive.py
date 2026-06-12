"""Task lifecycle store operations — split out of tasks.py so neither file
exceeds the function-count ceiling. Imports tasks lazily inside each function
to avoid an import cycle (tasks re-exports these names at its module bottom).
"""
from __future__ import annotations


def next_task() -> dict | None:
    """The next task to work: the active in_progress task, else any other
    in_progress, else the first dependency-ready pending task, else (if every
    pending task is blocked) the first pending task."""
    from inertia_forge.tasks import active_task_id, get_task, list_tasks
    active = active_task_id()
    if active and (a := get_task(active)) and a["status"] == "in_progress":
        return a
    for tk in list_tasks():
        if tk["status"] == "in_progress":
            return tk
    from inertia_forge.taskgraph import ready_tasks
    if ready := ready_tasks():
        return ready[0]
    for tk in list_tasks():
        if tk["status"] == "pending":
            return tk
    return None


def archive_task(task_id: str) -> bool:
    from inertia_forge.tasks import load, save
    data = load()
    if task_id not in data["tasks"]:
        return False
    data["archived"][task_id] = data["tasks"].pop(task_id)
    if data.get("active_task") == task_id:
        data["active_task"] = None
    save(data)
    return True


def restore_task(task_id: str) -> bool:
    from inertia_forge.tasks import load, save
    data = load()
    if task_id not in data["archived"]:
        return False
    data["tasks"][task_id] = data["archived"].pop(task_id)
    save(data)
    return True


def list_archived() -> list[dict]:
    from inertia_forge.tasks import load
    data = load()
    return [data["archived"][k] for k in sorted(data["archived"])]


def cleanup_done() -> int:
    """Archive every done task. Returns the count archived."""
    from inertia_forge.tasks import load, save
    data = load()
    done = [tid for tid, t in data["tasks"].items() if t.get("status") == "done"]
    for tid in done:
        data["archived"][tid] = data["tasks"].pop(tid)
        if data.get("active_task") == tid:
            data["active_task"] = None
    save(data)
    return len(done)
