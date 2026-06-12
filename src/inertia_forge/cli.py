"""inertia-forge command-line interface.

  inertia-forge init [--target DIR]   install Claude Code hooks into a project
  inertia-forge skills [validate]      list / validate the skill registry
  inertia-forge start <skill> <target> start a forge session
  inertia-forge record-phase <p> <t>   record a phase (auto-closes on all-green)
  inertia-forge status                 forge session + plan/tasks + last/next
  inertia-forge close                  close (refuses while gates remain)
  inertia-forge arch <path>            deterministic architecture check
  inertia-forge verify [dir] [--cov P] run pytest + report pass/fail/coverage
  inertia-forge check [path] [--tests] project gate: arch + secrets (+ tests)
  inertia-forge task ...               manage the native task store
  inertia-forge state [--done/--next]  session-continuity ledger
  inertia-forge log [--claims]         view the audit trail
  inertia-forge pack                   bundle context to .forge/context_pack.md
  inertia-forge read <skill>           mark a skill's methodology doc as read
"""
from __future__ import annotations

import sys


def _list_skills() -> int:
    from inertia_forge.skill_registry import (
        get_all_skills,
        get_evidence_mode,
        get_required_steps,
    )
    for name in sorted(get_all_skills()):
        mode = get_evidence_mode(name)
        gates = get_required_steps(name)
        print(f"  {name:26} {mode:15} blocking_gates={gates}")
    return 0


# command -> (module, function). Lazy-imported so the CLI stays fast.
_DISPATCH = {
    "init": ("inertia_forge.init", "run_init"),
    "task": ("inertia_forge.task_cli", "run_task"),
    "arch": ("inertia_forge.commands", "run_arch"),
    "verify": ("inertia_forge.commands", "run_verify"),
    "check": ("inertia_forge.commands", "run_check"),
    "state": ("inertia_forge.commands", "run_state"),
    "status": ("inertia_forge.commands", "run_status"),
    "log": ("inertia_forge.commands", "run_log"),
    "read": ("inertia_forge.commands", "run_read"),
    "pack": ("inertia_forge.commands", "run_pack"),
    "scan-deps": ("inertia_forge.commands", "run_scan_deps"),
    "doctor": ("inertia_forge.doctor", "run_doctor"),
    "sweep": ("inertia_forge.sweep", "run_sweep"),
    "metrics": ("inertia_forge.metrics", "run_metrics"),
    "ignite": ("inertia_forge.ignite", "run_ignite"),
    "agents": ("inertia_forge.assets", "run_agents"),
    "memory": ("inertia_forge.memory", "run_memory"),
    "capabilities": ("inertia_forge.capabilities", "run_capabilities"),
    "sandbox": ("inertia_forge.sandbox", "run_sandbox"),
    "intent": ("inertia_forge.intent", "run_intent"),
    "orchestrate": ("inertia_forge.orchestrate", "run_orchestrate"),
    "benchmark": ("inertia_forge.benchmark", "run_benchmark"),
    "config": ("inertia_forge.config", "run_config"),
    "feature": ("inertia_forge.feature", "run_feature"),
    "learn": ("inertia_forge.learn", "run_learn"),
    "standup": ("inertia_forge.standup", "run_standup"),
    "contain": ("inertia_forge.containment", "run_contain"),
    "timer": ("inertia_forge.timer", "run_timer"),
    "cache": ("inertia_forge.cache", "run_cache"),
    "subagent": ("inertia_forge.subagent", "run_subagent"),
    "template": ("inertia_forge.template", "run_template"),
    "migrate": ("inertia_forge.migrate", "run_migrate"),
    "mcp": ("inertia_forge.mcp", "run_mcp"),
    "gaps": ("inertia_forge.gaps", "run_gaps"),
    "release": ("inertia_forge.release", "run_release"),
    "sprint": ("inertia_forge.sprint", "run_sprint"),
    "feedback": ("inertia_forge.feedback", "run_feedback"),
    "wizard": ("inertia_forge.wizard", "run_wizard"),
    "install-hook": ("inertia_forge.commands", "run_install_hook"),
    "audit": ("inertia_forge.audit", "run_audit"),
    "compaction": ("inertia_forge.compaction", "run_compaction"),
    "banner": ("inertia_forge.show", "run_banner"),
    "logo": ("inertia_forge.show", "run_logo"),
    "statusline": ("inertia_forge.statusline", "run_statusline"),
    "role": ("inertia_forge.roles", "run_role"),
    "targeted": ("inertia_forge.targeted", "run_targeted"),
    "consistency": ("inertia_forge.consistency", "run_consistency"),
    "preset": ("inertia_forge.presets", "run_preset"),
    "verify-commit": ("inertia_forge.gitcheck", "run_verify_commit"),
    "verify-output": ("inertia_forge.gitcheck", "run_verify_output"),
    "tokens": ("inertia_forge.tokens", "run_tokens"),
    "freshness": ("inertia_forge.freshness", "run_freshness"),
    "scope": ("inertia_forge.scope", "run_scope"),
    "backlog": ("inertia_forge.backlog", "run_backlog"),
    "plan": ("inertia_forge.plan", "run_plan"),
    "handoff": ("inertia_forge.handoff", "run_handoff"),
    "prune": ("inertia_forge.retention", "run_prune"),
    "json": ("inertia_forge.jsonout", "run_json"),
    "preflight": ("inertia_forge.preflight", "run_preflight"),
    "validate-store": ("inertia_forge.storecheck", "run_validate_store"),
    "dead-code": ("inertia_forge.deadcode", "run_dead_code"),
    "review": ("inertia_forge.review", "run_review"),
    "diff": ("inertia_forge.diffstat", "run_diff"),
    "vet": ("inertia_forge.vet", "run_vet"),
    "complexity": ("inertia_forge.complexity", "run_complexity"),
    "imports": ("inertia_forge.importgraph", "run_imports"),
    "docs": ("inertia_forge.docstrings", "run_docs"),
    "types": ("inertia_forge.typehints", "run_types"),
    "changelog": ("inertia_forge.changelog", "run_changelog"),
    "coverage": ("inertia_forge.coverage", "run_coverage"),
    "run": ("inertia_forge.tools", "run_exec"),
    "write": ("inertia_forge.tools", "run_write"),
    "edit": ("inertia_forge.tools", "run_edit"),
    "view": ("inertia_forge.tools", "run_view"),
    "qc": ("inertia_forge.qc", "run_qc"),
    "telemetry": ("inertia_forge.telemetry", "run_telemetry"),
    "semantic": ("inertia_forge.semantic", "run_semantic"),
    "suggest-split": ("inertia_forge.splitter", "run_suggest_split"),
    "calibrate": ("inertia_forge.calibrate_cli", "run_calibrate"),
    "models": ("inertia_forge.models", "run_models"),
    "invoke": ("inertia_forge.agent", "run_invoke"),
    "dispatch": ("inertia_forge.invoker", "run_dispatch"),
    "engage": ("inertia_forge.engage_cli", "run_engage"),
    "query": ("inertia_forge.query", "run_query"),
    "xref": ("inertia_forge.xref", "run_xref"),
    "scan": ("inertia_forge.scan", "run_scan"),
    "policy": ("inertia_forge.policy", "run_policy"),
    "mermaid": ("inertia_forge.mermaid", "run_mermaid"),
    "report": ("inertia_forge.report", "run_report"),
}


def _run_skills(argv: list[str]) -> int:
    if len(argv) > 1 and argv[1] == "validate":
        from inertia_forge.validate import run_validate
        return run_validate()
    if len(argv) > 1 and argv[1] == "export":
        from inertia_forge.export import run_export
        return run_export(argv[2:])
    if len(argv) > 1 and argv[1] == "new":
        from inertia_forge.skill_authoring import run_skill_new
        return run_skill_new(argv[2:])
    if len(argv) > 1 and argv[1] == "score":
        from inertia_forge.skill_authoring import run_skill_score
        return run_skill_score(argv[2:])
    if len(argv) > 1 and argv[1] == "search":
        from inertia_forge.recommend import run_search
        return run_search(argv[2:])
    return _list_skills()


def main(argv: list[str] | None = None) -> int:
    import importlib

    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else ""

    if cmd in ("skills", "list"):
        return _run_skills(argv)
    if cmd in _DISPATCH:
        mod, fn = _DISPATCH[cmd]
        return getattr(importlib.import_module(mod), fn)(argv[1:])

    # Delegate session lifecycle (start / record-phase / close) to the bridge.
    from inertia_forge.skill_bridge import main as bridge_main
    return bridge_main(argv)


if __name__ == "__main__":
    sys.exit(main())
