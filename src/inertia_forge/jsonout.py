"""`inertia-forge json <query>` — machine-readable forge state for agents.

Each query maps to a pure read of the stores and returns a JSON envelope (see
inertia_forge.envelope). One front door for programmatic consumption — no need
to thread a --json flag through every command.

  status        forge session + plan + task rollup + continuity
  tasks         the full task list
  graph         ready / blocked / waves / cycle / missing-deps
  plan          token projection from remaining complexity
  consistency   store-invariant issues (envelope status reflects ok/error)
  freshness     stale / missing continuity files
  budget        complexity rollup by status
"""
from __future__ import annotations

import argparse


def _status() -> tuple[dict, list[str]]:
    from inertia_forge import state as st, tasks as tk
    from inertia_forge.completion_lock import get_forge_status
    tasks = tk.list_tasks()
    data = st.load()
    return {
        "forge": get_forge_status(),
        "plan": tk.get_plan(),
        "active_task": tk.active_task_id(),
        "tasks": {"total": len(tasks),
                  "done": sum(1 for x in tasks if x["status"] == "done")},
        "last": data["last"], "next": data["next"],
    }, []


def _tasks() -> tuple[list, list[str]]:
    from inertia_forge import tasks as tk
    return tk.list_tasks(), []


def _graph() -> tuple[dict, list[str]]:
    from inertia_forge import taskgraph as tg
    return {"ready": [x["id"] for x in tg.ready_tasks()],
            "blocked": tg.blocked_tasks(), "waves": tg.parallel_waves(),
            "cycle": tg.find_cycle(), "missing_deps": tg.missing_deps()}, []


def _plan() -> tuple[dict, list[str]]:
    from inertia_forge.plan import estimate_plan
    return estimate_plan(), []


def _consistency() -> tuple[dict, list[str]]:
    from inertia_forge.consistency import issues
    iss = issues()
    return {"consistent": not iss, "issues": iss}, iss


def _freshness() -> tuple[dict, list[str]]:
    from pathlib import Path
    from inertia_forge.freshness import stale_files
    stale = stale_files(Path("."))
    return {"stale": stale, "fresh": not stale}, []


def _budget() -> tuple[dict, list[str]]:
    from inertia_forge import tasks as tk
    by_status: dict[str, float] = {}
    for x in tk.list_tasks():
        by_status[x["status"]] = by_status.get(x["status"], 0) + x.get("complexity", 0)
    return {"by_status": by_status, "total": sum(by_status.values())}, []


_QUERIES = {
    "status": _status, "tasks": _tasks, "graph": _graph, "plan": _plan,
    "consistency": _consistency, "freshness": _freshness, "budget": _budget,
}


def run_json(argv: list[str]) -> int:
    from inertia_forge.envelope import emit, wrap_error, wrap_ok
    p = argparse.ArgumentParser(prog="inertia-forge json")
    p.add_argument("query", choices=sorted(_QUERIES))
    args = p.parse_args(argv)
    try:
        data, errors = _QUERIES[args.query]()
    except Exception as e:  # never crash a machine consumer mid-parse
        return emit(wrap_error(f"{type(e).__name__}: {e}"))
    if errors:
        env = wrap_error(f"{len(errors)} issue(s)", data)
        env["errors"] = errors
        return emit(env)
    return emit(wrap_ok(data))
