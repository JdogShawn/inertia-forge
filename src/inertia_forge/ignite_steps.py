"""Per-task steps for the ignite loop — build the driver prompt, dispatch to an
agent (the opt-in LLM bridge), mark the store done, and record the outcome.

The default task runner is the one place ignite touches an LLM. Pass your own
``task_runner`` (or ``--dry-run``) to drive the whole loop with zero LLM calls —
the deterministic core stays intact.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

DRIVER_TOOLS = ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]


def build_task_prompt(task: dict, test_instruction: str = "") -> str:
    """A TDD driver instruction from a native task (title · AC · verification)."""
    lines = [
        f"Implement task {task['id']}: {task.get('title', '')}".rstrip(),
        "",
        "Follow test-driven development: write failing tests first, then the",
        "minimal code to pass them, then refactor.",
        "",
        "Acceptance criteria:",
    ]
    for ac in task.get("acceptance_criteria", []):
        mark = "x" if ac.get("done") else " "
        lines.append(f"  - [{mark}] {ac['text']}")
    verification = task.get("verification", "")
    if verification:
        lines += ["", f"Verification (must pass): {verification}"]
    scope = task.get("scope") or []
    if scope:
        lines += ["", "Touch only these paths: " + ", ".join(scope)]
    if test_instruction:
        lines += ["", test_instruction]
    return "\n".join(lines)


def resolve_model(task: dict, config) -> str | None:
    """The model for a task — routed by its complexity, else the fixed model.

    `config.model_routing` is {tier: {"max": ceiling, "model": name}}; the first
    tier whose ceiling >= the task's complexity wins. No routing → config.model.
    """
    routing = getattr(config, "model_routing", None)
    if not routing:
        return config.model
    cx = float(task.get("complexity", 0) or 0)
    for tier in sorted(routing.values(), key=lambda d: d.get("max", 0)):
        if cx <= tier.get("max", 0):
            return tier.get("model")
    return config.model


def agent_task_runner(task: dict, config) -> bool:
    """Dispatch one task to the forge's implementation agent (Piston).

    Piston is the read-write TDD driver from the bundled roster; its own `.md`
    system prompt drives the work. LLM-agnostic — runs on any CLI/model, with the
    model routed per task by complexity.
    """
    from inertia_forge.invoker import dispatch
    resp = dispatch("piston", build_task_prompt(task, config.test_instruction),
                    cli=config.agent, model=resolve_model(task, config),
                    working_dir=config.project_root, token_budget=config.token_budget)
    return not resp.is_error


def mark_task_done(task_id: str) -> None:
    """Set a task done in the store (ignite-level done: executed + verified)."""
    from inertia_forge import tasks as t
    data = t.load()
    task = data["tasks"].get(task_id)
    if task is None:
        return
    for ac in task.get("acceptance_criteria", []):
        ac["done"] = True
    task["status"] = "done"
    task["completed_at"] = datetime.now(timezone.utc).isoformat()
    t.save(data)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_outcome(task: dict, outcome: str, duration: float) -> None:
    """Record an ignite task outcome to telemetry and the calibration loop."""
    tid = task.get("id", "")
    complexity = float(task.get("complexity", 0) or 0)
    try:
        from inertia_forge.telemetry import record as trecord
        trecord("ignite", tid, duration,
                {"outcome": outcome, "complexity": complexity})
    except Exception:
        pass
    if outcome in ("success", "skipped") and complexity:
        try:
            from inertia_forge import calibrate
            calibrate.record(complexity, complexity, label=tid, task_type="ignite",
                             duration_seconds=duration, outcome=outcome,
                             complexity=complexity)
        except Exception:
            pass


def verify_output(project_root: Path) -> bool:
    """True if the last commit carried meaningful (code/test/cli) changes."""
    from inertia_forge.gitcheck import meaningful_changes
    meaningful, _ = meaningful_changes(project_root, "HEAD~1")
    return bool(meaningful)
