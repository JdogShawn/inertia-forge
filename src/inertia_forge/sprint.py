"""Sprints — named groups of tasks (`.forge/sprints.json`). Deterministic.

A sprint bundles a set of task IDs under a name, tracks an active sprint, and
reports completion against the native task store.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SPRINTS = Path(".forge") / "sprints.json"


def _load() -> dict:
    if SPRINTS.exists():
        try:
            d = json.loads(SPRINTS.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            d = {}
    else:
        d = {}
    d.setdefault("active", None)
    d.setdefault("sprints", {})
    return d


def _save(d: dict) -> None:
    SPRINTS.parent.mkdir(parents=True, exist_ok=True)
    SPRINTS.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def start(name: str) -> None:
    d = _load()
    d["sprints"].setdefault(name, {"tasks": [], "done": False})
    d["active"] = name
    _save(d)


def add_task(task_id: str, name: str | None = None) -> bool:
    d = _load()
    name = name or d["active"]
    if name is None or name not in d["sprints"]:
        return False
    if task_id not in d["sprints"][name]["tasks"]:
        d["sprints"][name]["tasks"].append(task_id)
    _save(d)
    return True


def complete(name: str | None = None) -> bool:
    d = _load()
    name = name or d["active"]
    if name is None or name not in d["sprints"]:
        return False
    d["sprints"][name]["done"] = True
    if d["active"] == name:
        d["active"] = None
    _save(d)
    return True


def _progress(task_ids: list[str]) -> str:
    from inertia_forge import tasks as t
    done = sum(1 for tid in task_ids if (tk := t.get_task(tid)) and tk["status"] == "done")
    return f"{done}/{len(task_ids)} done"


def run_sprint(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge sprint")
    sub = p.add_subparsers(dest="sub", required=True)
    st = sub.add_parser("start"); st.add_argument("name")
    ad = sub.add_parser("add"); ad.add_argument("task_id"); ad.add_argument("--sprint")
    cp = sub.add_parser("complete"); cp.add_argument("name", nargs="?")
    sub.add_parser("list")
    args = p.parse_args(argv)
    if args.sub == "start":
        start(args.name); print(f"sprint '{args.name}' active")
        return 0
    if args.sub == "add":
        ok = add_task(args.task_id, args.sprint)
        print(f"added {args.task_id}" if ok else "no active sprint")
        return 0 if ok else 1
    if args.sub == "complete":
        ok = complete(args.name)
        print("sprint completed" if ok else "no such sprint")
        return 0 if ok else 1
    d = _load()
    if not d["sprints"]:
        print("(no sprints)")
        return 0
    for name, s in sorted(d["sprints"].items()):
        mark = "*" if name == d["active"] else ("x" if s["done"] else " ")
        print(f"  [{mark}] {name:20} {_progress(s['tasks'])}")
    return 0
