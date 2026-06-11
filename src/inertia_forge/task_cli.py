"""`inertia-forge task ...` — manage the native forge task store.

  task plan  --type feature --title "..."          create/replace the plan
  task add   T1.1 --title "..." --complexity 5 \
             --ac "does X" --ac "does Y" --verify "pytest tests/x"
  task start T1.1                                   set active + in_progress
  task ac    T1.1 0                                 check acceptance criterion 0
  task ac    T1.1 --all                             check every criterion
  task done  T1.1                                   complete (needs all AC met)
  task list                                         list tasks
  task show  T1.1                                   show one task
"""
from __future__ import annotations

import argparse

from inertia_forge import tasks as t


def _h_plan(a: argparse.Namespace) -> int:
    plan = t.create_plan(a.type, a.title, a.id)
    print(f"plan: {plan['id']} ({plan['type']}) — {plan['title']}")
    return 0


def _h_add(a: argparse.Namespace) -> int:
    task = t.add_task(a.id, a.title, a.complexity, a.ac or [], a.verify)
    print(f"added {task['id']} (complexity {task['complexity']:g}, "
          f"{len(task['acceptance_criteria'])} AC)")
    return 0


def _h_start(a: argparse.Namespace) -> int:
    t.start_task(a.id)
    print(f"started {a.id} (active, in_progress)")
    return 0


def _h_ac(a: argparse.Namespace) -> int:
    task = t.get_task(a.id)
    if task is None:
        print(f"no such task: {a.id}")
        return 1
    indices = range(len(task["acceptance_criteria"])) if a.all else [a.index]
    for i in indices:
        t.check_ac(a.id, i)
    print(f"checked {'all' if a.all else a.index} AC on {a.id}")
    return 0


def _h_done(a: argparse.Namespace) -> int:
    t.complete_task(a.id)
    print(f"completed {a.id}")
    return 0


def _h_list(_a: argparse.Namespace) -> int:
    active = t.active_task_id()
    tasks = t.list_tasks()
    if not tasks:
        print("(no tasks)")
        return 0
    for x in tasks:
        met = sum(1 for c in x["acceptance_criteria"] if c["done"])
        mark = "*" if x["id"] == active else " "
        print(f"{mark} {x['id']:8} {x['status']:12} AC {met}/{len(x['acceptance_criteria'])}  {x['title']}")
    return 0


def _h_budget(_a: argparse.Namespace) -> int:
    tasks = t.list_tasks()
    if not tasks:
        print("(no tasks)")
        return 0
    total = sum(x.get("complexity", 0) for x in tasks)
    by_status: dict[str, float] = {}
    for x in tasks:
        by_status[x["status"]] = by_status.get(x["status"], 0) + x.get("complexity", 0)
    unestimated = [x["id"] for x in tasks if not 0 <= x.get("complexity", -1) <= 100]
    print(f"total complexity: {total:g} across {len(tasks)} task(s)")
    for s in ("pending", "in_progress", "done"):
        if s in by_status:
            print(f"  {s:12} {by_status[s]:g}")
    if unestimated:
        print(f"unestimated / out-of-range: {', '.join(unestimated)}")
    return 0


def _h_show(a: argparse.Namespace) -> int:
    task = t.get_task(a.id)
    if task is None:
        print(f"no such task: {a.id}")
        return 1
    print(f"{task['id']}  [{task['status']}]  complexity={task['complexity']:g}")
    print(f"  {task['title']}")
    for i, c in enumerate(task["acceptance_criteria"]):
        print(f"  [{'x' if c['done'] else ' '}] {i}: {c['text']}")
    print(f"  verify: {task['verification']}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="inertia-forge task")
    sub = p.add_subparsers(dest="sub", required=True)

    pl = sub.add_parser("plan", help="create/replace the plan")
    pl.add_argument("--type", required=True, choices=t.VALID_PLAN_TYPES)
    pl.add_argument("--title", required=True)
    pl.add_argument("--id", default="p1")
    pl.set_defaults(fn=_h_plan)

    ad = sub.add_parser("add", help="add a task")
    ad.add_argument("id")
    ad.add_argument("--title", required=True)
    ad.add_argument("--complexity", type=float, required=True)
    ad.add_argument("--ac", action="append", help="acceptance criterion (repeatable)")
    ad.add_argument("--verify", required=True, help="verification (test) command")
    ad.set_defaults(fn=_h_add)

    st = sub.add_parser("start", help="set active + in_progress")
    st.add_argument("id")
    st.set_defaults(fn=_h_start)

    ac = sub.add_parser("ac", help="check acceptance criteria")
    ac.add_argument("id")
    ac.add_argument("index", type=int, nargs="?", default=0)
    ac.add_argument("--all", action="store_true")
    ac.set_defaults(fn=_h_ac)

    dn = sub.add_parser("done", help="complete a task (needs all AC met)")
    dn.add_argument("id")
    dn.set_defaults(fn=_h_done)

    sub.add_parser("list", help="list tasks").set_defaults(fn=_h_list)
    sub.add_parser("budget", help="complexity rollup").set_defaults(fn=_h_budget)

    sh = sub.add_parser("show", help="show one task")
    sh.add_argument("id")
    sh.set_defaults(fn=_h_show)
    return p


def run_task(argv: list[str]) -> int:
    args = _build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except ValueError as e:
        print(f"error: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_task(sys.argv[1:]))
