"""Deterministic backlog ingest — parse a markdown backlog into the task store.

This is the *ingest* half of bpsai-pair's `engage` (the autonomous agent
execution stays out — the forge is no-LLM; agents do the work, the forge tracks
it). Parsing is pure regex, fully deterministic.

Backlog format::

    # Plan Title
    type: feature

    ## T1.1: Cart totals
    complexity: 8
    - [ ] totals are correct
    - [ ] tests pass
    verify: pytest tests/cart

`## T<sprint>.<seq>: title` starts a task; `- [ ]`/`- [x]` lines are
acceptance criteria; `complexity:` and `verify:` are per-task fields.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from inertia_forge import tasks as t

_TASK_HDR = re.compile(r"^##\s+(T\d+\.\d+)\s*[:\-]?\s*(.*)$")
_AC = re.compile(r"^\s*-\s*\[[ xX]\]\s*(.+)$")
_FIELD = re.compile(r"^(complexity|verify|type)\s*:\s*(.+)$", re.IGNORECASE)


def parse_backlog(text: str) -> tuple[dict, list[dict]]:
    """Return (plan, tasks). Pure, deterministic."""
    plan = {"title": "Backlog", "type": "feature"}
    tasks: list[dict] = []
    cur: dict | None = None
    for line in text.splitlines():
        hdr = _TASK_HDR.match(line)
        if hdr:
            cur = {"id": hdr.group(1), "title": hdr.group(2).strip() or hdr.group(1),
                   "complexity": 0.0, "ac": [], "verify": ""}
            tasks.append(cur)
            continue
        if line.startswith("# ") and cur is None:
            plan["title"] = line[2:].strip()
            continue
        ac = _AC.match(line)
        if ac and cur is not None:
            cur["ac"].append(ac.group(1).strip())
            continue
        field = _FIELD.match(line)
        if field:
            key, val = field.group(1).lower(), field.group(2).strip()
            if key == "type" and cur is None:
                plan["type"] = val
            elif key == "complexity" and cur is not None:
                cur["complexity"] = float(val) if val.replace(".", "", 1).isdigit() else 0.0
            elif key == "verify" and cur is not None:
                cur["verify"] = val
    return plan, tasks


def run_engage(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="inertia-forge engage")
    parser.add_argument("backlog", help="path to a backlog .md file")
    args = parser.parse_args(argv)
    path = Path(args.backlog)
    if not path.is_file():
        print(f"backlog not found: {path}")
        return 1
    plan, parsed = parse_backlog(path.read_text(encoding="utf-8"))
    t.create_plan(plan["type"] if plan["type"] in t.VALID_PLAN_TYPES else "feature", plan["title"])
    created, errors = 0, []
    for task in parsed:
        try:
            t.add_task(task["id"], task["title"], task["complexity"], task["ac"], task["verify"])
            created += 1
        except ValueError as e:
            errors.append(f"{task['id']}: {e}")
    print(f"plan '{plan['title']}' ({plan['type']}) — {created} task(s) ingested")
    for e in errors:
        print(f"  SKIPPED {e}")
    return 1 if errors else 0
