"""Task dependency graph — ready / blocked / topological order / parallel waves.

Tasks carry a ``depends_on`` list of task ids. This module reads the store and
answers the scheduling questions deterministically: which tasks are ready to
start (every dependency done), which are blocked and by what, a dependency-
respecting order, the parallel waves (Kahn levels — "what N agents can run at
once"), and whether the graph has a cycle. Pure set math over the on-disk
store, no LLM.
"""
from __future__ import annotations

from inertia_forge import tasks as t


def _by_id() -> dict[str, dict]:
    return {x["id"]: x for x in t.list_tasks()}


def deps_of(task: dict) -> list[str]:
    return list(task.get("depends_on", []))


def missing_deps() -> dict[str, list[str]]:
    """task id → dependency ids that reference no existing task."""
    tasks = _by_id()
    return {tid: absent for tid, task in tasks.items()
            if (absent := [d for d in deps_of(task) if d not in tasks])}


def find_cycle() -> list[str] | None:
    """Return one dependency cycle as an id path, or None if acyclic."""
    tasks = _by_id()
    color: dict[str, int] = {tid: 0 for tid in tasks}  # 0 white, 1 gray, 2 black
    stack: list[str] = []

    def visit(tid: str) -> list[str] | None:
        color[tid] = 1
        stack.append(tid)
        for d in deps_of(tasks[tid]):
            if d not in tasks:
                continue
            if color[d] == 1:
                return stack[stack.index(d):] + [d]
            if color[d] == 0 and (cyc := visit(d)):
                return cyc
        color[tid] = 2
        stack.pop()
        return None

    for tid in tasks:
        if color[tid] == 0 and (cyc := visit(tid)):
            return cyc
    return None


def ready_tasks() -> list[dict]:
    """Pending tasks whose every existing dependency is done."""
    tasks = _by_id()
    return [task for task in t.list_tasks()
            if task["status"] == "pending"
            and all(tasks.get(d, {}).get("status") == "done" for d in deps_of(task))]


def blocked_tasks() -> dict[str, list[str]]:
    """Pending task id → the dep ids still blocking it (unmet or missing)."""
    tasks = _by_id()
    out: dict[str, list[str]] = {}
    for task in t.list_tasks():
        if task["status"] != "pending":
            continue
        unmet = [d for d in deps_of(task) if tasks.get(d, {}).get("status") != "done"]
        if unmet:
            out[task["id"]] = unmet
    return out


def parallel_waves() -> list[list[str]]:
    """Kahn levels: each wave is the task ids whose deps all sit in earlier
    waves. Tasks in a cycle (or transitively depending on a cycle) are omitted."""
    tasks = _by_id()
    edges = {tid: [d for d in deps_of(task) if d in tasks] for tid, task in tasks.items()}
    placed: set[str] = set()
    waves: list[list[str]] = []
    while len(placed) < len(tasks):
        wave = sorted(tid for tid in tasks
                      if tid not in placed and all(d in placed for d in edges[tid]))
        if not wave:
            break  # remaining ids are in a cycle
        waves.append(wave)
        placed.update(wave)
    return waves


def topo_order() -> list[str]:
    """A dependency-respecting linear order (flatten of the parallel waves)."""
    return [tid for wave in parallel_waves() for tid in wave]
