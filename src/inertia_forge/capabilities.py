"""`inertia-forge capabilities` — what the forge can do (discovery manifest).

A single, machine- or human-readable surface an LLM can read to learn the whole
toolkit: commands, the agent roster, the gated skills + their evidence modes,
and the evidence modes themselves. Deterministic — generated from the registry.
"""
from __future__ import annotations

import argparse
import json

_COMMAND_GROUPS = {
    "gates": ["arch", "check", "verify", "sweep", "scan-deps"],
    "tasks & planning": ["task", "ignite", "feature", "intent"],
    "session lifecycle": ["start", "record-phase", "status", "close", "doctor"],
    "continuity & audit": ["state", "standup", "pack", "log", "memory", "cache"],
    "agents & skills": ["agents", "skills", "read"],
    "enforcement": ["contain", "sandbox", "orchestrate", "init"],
    "ops": ["metrics", "timer", "config", "benchmark", "template", "migrate", "mcp", "capabilities"],
}


def manifest() -> dict:
    from inertia_forge import __version__, assets
    from inertia_forge.evidence_collectors import _KNOWN_EVIDENCE_MODES
    from inertia_forge.skill_registry import get_all_skills, get_evidence_mode

    return {
        "name": "inertia-forge",
        "version": __version__,
        "deterministic": True,
        "llm_calls": 0,
        "commands": _COMMAND_GROUPS,
        "agents": assets.agent_names(),
        "skills": {n: get_evidence_mode(n) for n in sorted(get_all_skills())},
        "evidence_modes": list(_KNOWN_EVIDENCE_MODES),
    }


def run_capabilities(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="inertia-forge capabilities")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    m = manifest()
    if args.json:
        print(json.dumps(m, indent=2))
        return 0
    print(f"inertia-forge {m['version']} — deterministic, zero LLM calls\n")
    for group, cmds in m["commands"].items():
        print(f"  {group:20} {' '.join(cmds)}")
    print(f"\n  agents               {' '.join(m['agents'])}")
    print(f"  evidence modes       {' '.join(m['evidence_modes'])}")
    print(f"  skills               {len(m['skills'])} registered")
    return 0
