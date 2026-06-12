"""Task-graph subcommands — deps / ready / graph. Split from task_cli to keep
both files under the function-count ceiling.
"""
from __future__ import annotations

import argparse

from inertia_forge import taskgraph as tg, tasks as t


def h_deps(a: argparse.Namespace) -> int:
    ids = [] if a.clear else a.on
    t.update_task(a.id, depends_on=ids)
    print(f"{a.id} depends on: {', '.join(ids) or '(none)'}")
    return 0


def h_ready(_a: argparse.Namespace) -> int:
    from inertia_forge.glyphs import g
    from inertia_forge.palette import paint
    ready = tg.ready_tasks()
    if not ready:
        print("(no ready tasks — all blocked, done, or none)")
        return 0
    for x in ready:
        print(f"  {paint(g('orbit'), 'go', bold=True)} {x['id']}  {x['title']}")
    return 0


def h_graph(_a: argparse.Namespace) -> int:
    from inertia_forge.glyphs import g, seal
    from inertia_forge.palette import paint
    arrow_r, arrow_l = g("arrow_r"), g("arrow_l")
    cyc = tg.find_cycle()
    if cyc:
        print(f"{seal('error')} dependency cycle: {(' ' + arrow_r + ' ').join(cyc)}")
    for tid, absent in sorted(tg.missing_deps().items()):
        print(f"{seal('warn')} {tid} depends on missing: {', '.join(absent)}")
    for i, wave in enumerate(tg.parallel_waves(), 1):
        print(f"  {paint(f'wave {i}', 'accent', bold=True)}: {', '.join(wave)}")
    blocked = tg.blocked_tasks()
    if blocked:
        print(paint("blocked:", "warn"))
        for tid, by in sorted(blocked.items()):
            print(f"  {tid} {arrow_l} {', '.join(by)}")
    return 1 if cyc else 0


def h_estimate(a: argparse.Namespace) -> int:
    from inertia_forge.estimate import estimate
    task = t.get_task(a.id)
    if task is None:
        print(f"no such task: {a.id}")
        return 1
    est = estimate(task)
    if a.apply:
        t.update_task(a.id, complexity=est)
        print(f"{a.id} complexity set to {est:g}")
    else:
        print(f"{a.id} estimated complexity: {est:g} (was {task.get('complexity', 0):g})")
    return 0


def h_audit(_a: argparse.Namespace) -> int:
    from inertia_forge.consistency import run_consistency
    return run_consistency([])


def add_parsers(sub) -> None:
    d = sub.add_parser("deps", help="set a task's dependencies")
    d.add_argument("id")
    d.add_argument("--on", nargs="*", default=[], help="task ids this one depends on")
    d.add_argument("--clear", action="store_true", help="clear all dependencies")
    d.set_defaults(fn=h_deps)
    sub.add_parser("ready", help="tasks whose deps are all done").set_defaults(fn=h_ready)
    sub.add_parser("graph", help="dependency waves + blocked + cycles").set_defaults(fn=h_graph)
    es = sub.add_parser("estimate", help="heuristic complexity estimate")
    es.add_argument("id")
    es.add_argument("--apply", action="store_true", help="write the estimate to the task")
    es.set_defaults(fn=h_estimate)
    sub.add_parser("audit", help="task-store consistency check").set_defaults(fn=h_audit)
