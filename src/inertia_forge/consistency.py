"""Task-store consistency checks — drift the store should never contain.

Deterministic invariants: a done task with unmet acceptance criteria, an active
task that isn't in_progress (or doesn't exist), self-dependencies, dangling or
duplicate dependencies, and dependency cycles. `consistency` (and `task audit`)
surface them and exit 1 on any finding, so the check can gate a commit.
"""
from __future__ import annotations

from inertia_forge import taskgraph as tg, tasks as t


def issues() -> list[str]:
    """Every consistency problem in the store, as human-readable lines."""
    out: list[str] = []
    tasks = t.list_tasks()
    ids = {x["id"] for x in tasks}
    for x in tasks:
        if x["status"] == "done" and any(not c["done"] for c in x["acceptance_criteria"]):
            out.append(f"{x['id']}: marked done but has unmet acceptance criteria")
        deps = x.get("depends_on", [])
        for d in deps:
            if d == x["id"]:
                out.append(f"{x['id']}: depends on itself")
            elif d not in ids:
                out.append(f"{x['id']}: depends on missing task {d}")
        if len(set(deps)) != len(deps):
            out.append(f"{x['id']}: duplicate entries in depends_on")
    active = t.active_task_id()
    if active and active not in ids:
        out.append(f"active task {active} does not exist")
    elif active and (a := t.get_task(active)) and a["status"] != "in_progress":
        out.append(f"active task {active} is {a['status']}, not in_progress")
    if cyc := tg.find_cycle():
        from inertia_forge.glyphs import g
        out.append("dependency cycle: " + (" " + g("arrow_r") + " ").join(cyc))
    return out


def run_consistency(_argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    found = issues()
    if not found:
        print(f"{seal('ok')} tasks consistent")
        return 0
    for msg in found:
        print(f"{seal('error')} {msg}")
    return 1
