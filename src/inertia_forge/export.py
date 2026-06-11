"""`inertia-forge skills export` — machine/human-readable registry export.

Makes the skill registry portable: JSON for tooling, Markdown for docs/sharing
with another agent or teammate.
"""
from __future__ import annotations

import argparse
import json


def _as_dict() -> dict:
    from inertia_forge.skill_registry import get_all_skills, get_evidence_mode

    out: dict = {}
    for name, s in get_all_skills().items():
        out[name] = {
            "evidence_mode": get_evidence_mode(name),
            "steps": list(s.steps),
            "gates": dict(s.gates),
            "loop_max": s.loop_max,
            "phase_evidence": dict(s.phase_evidence),
            "doc": s.doc,
        }
    return out


def run_export(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="inertia-forge skills export")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    args = parser.parse_args(argv)
    data = _as_dict()
    if args.format == "json":
        print(json.dumps(data, indent=2))
        return 0
    for name, d in data.items():
        blocking = [k for k, v in d["gates"].items() if v == "blocking"]
        print(f"## {name}  (`{d['evidence_mode']}`)")
        print(f"- steps: {', '.join(d['steps'])}")
        print(f"- blocking gates: {', '.join(blocking) or '(none)'}")
        print()
    return 0
