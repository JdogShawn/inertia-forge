"""`inertia-forge ignite <backlog.md>` — set a backlog in motion.

INERTIA's own name for "ingest a backlog and begin": a body at rest goes to
motion. Deterministic — parse a markdown backlog into the native plan + task
store, set the continuity ledger's "next", and suggest which agent picks up the
first task. (The agents do the work; the forge gates it. No LLM here.)

Backlog format::

    # Plan Title
    type: feature

    ## T1.1: Cart totals
    complexity: 8
    - [ ] totals are correct
    - [ ] tests pass
    verify: pytest tests/cart
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from inertia_forge import state as st, tasks as t

_TASK_HDR = re.compile(r"^##\s+(T\d+\.\d+)\s*[:\-]?\s*(.*)$")
_AC = re.compile(r"^\s*-\s*\[[ xX]\]\s*(.+)$")
_FIELD = re.compile(r"^(complexity|verify|type)\s*:\s*(.+)$", re.IGNORECASE)

# Which agent should pick up work classified to a given skill.
_SKILL_AGENT = {
    "implementing_with_tdd": "Piston",
    "designing_and_implementing": "Vector",
    "reviewing_code": "Caliper",
    "refactoring": "Piston",
    "releasing_versions": "Bastion",
    "security_audit": "Sentinel",
}


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


def _suggest_agent(plan: dict, first: dict) -> str:
    from inertia_forge.intent import classify
    skill = classify(f"{plan['title']} {first['title']}")["skill"]
    return _SKILL_AGENT.get(skill, "Piston")


def run_ignite(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="inertia-forge ignite")
    parser.add_argument("backlog", help="path to a backlog .md file")
    args = parser.parse_args(argv)
    path = Path(args.backlog)
    if not path.is_file():
        print(f"backlog not found: {path}")
        return 1
    plan, parsed = parse_backlog(path.read_text(encoding="utf-8"))
    ptype = plan["type"] if plan["type"] in t.VALID_PLAN_TYPES else "feature"
    t.create_plan(ptype, plan["title"])
    created, errors = [], []
    for task in parsed:
        try:
            t.add_task(task["id"], task["title"], task["complexity"], task["ac"], task["verify"])
            created.append(task)
        except ValueError as e:
            errors.append(f"{task['id']}: {e}")

    print(f"IGNITED: plan '{plan['title']}' ({ptype}) — {len(created)} task(s) in motion")
    if created:
        first = created[0]
        st.set_progress(next_=f"implement {first['title']}")
        print(f"  first:  {first['id']} — {first['title']}")
        print(f"  agent:  {_suggest_agent(plan, first)} (suggested)")
        print(f"  next:   implement {first['title']}")
    for e in errors:
        print(f"  SKIPPED {e}")
    return 1 if errors else 0
