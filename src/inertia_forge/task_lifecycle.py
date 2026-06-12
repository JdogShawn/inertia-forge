"""Task lifecycle subcommands — next / archive / restore / list-archived /
cleanup / changelog. Kept separate so task_cli stays under the function ceiling.
"""
from __future__ import annotations

import argparse

from inertia_forge import tasks as t


def h_next(_a: argparse.Namespace) -> int:
    nxt = t.next_task()
    if nxt is None:
        print("(no next task — add one, or all are done)")
        return 0
    print(f"next: {nxt['id']} [{nxt['status']}] — {nxt['title']}")
    return 0


def h_archive(a: argparse.Namespace) -> int:
    ok = t.archive_task(a.id)
    print(f"archived {a.id}" if ok else f"no such task: {a.id}")
    return 0 if ok else 1


def h_restore(a: argparse.Namespace) -> int:
    ok = t.restore_task(a.id)
    print(f"restored {a.id}" if ok else f"{a.id} not in archive")
    return 0 if ok else 1


def h_list_archived(_a: argparse.Namespace) -> int:
    arch = t.list_archived()
    if not arch:
        print("(no archived tasks)")
        return 0
    for x in arch:
        print(f"  {x['id']:8} [{x['status']}] {x['title']}")
    return 0


def h_cleanup(_a: argparse.Namespace) -> int:
    n = t.cleanup_done()
    print(f"archived {n} done task(s)")
    return 0


def h_changelog(_a: argparse.Namespace) -> int:
    done = [x for x in t.list_tasks() + t.list_archived() if x.get("status") == "done"]
    if not done:
        print("(no completed tasks)")
        return 0
    print("## Changelog\n")
    for x in sorted(done, key=lambda d: d.get("completed_at", "")):
        print(f"- {x['id']}: {x['title']}")
    return 0


def add_parsers(sub) -> None:
    """Register the lifecycle subcommands on a task subparser group."""
    sub.add_parser("next", help="the next task to work").set_defaults(fn=h_next)
    ar = sub.add_parser("archive"); ar.add_argument("id"); ar.set_defaults(fn=h_archive)
    rs = sub.add_parser("restore"); rs.add_argument("id"); rs.set_defaults(fn=h_restore)
    sub.add_parser("list-archived", help="list archived tasks").set_defaults(fn=h_list_archived)
    sub.add_parser("cleanup", help="archive all done tasks").set_defaults(fn=h_cleanup)
    sub.add_parser("changelog", help="changelog from completed tasks").set_defaults(fn=h_changelog)
