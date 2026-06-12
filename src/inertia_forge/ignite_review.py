"""Per-task review-and-fix loop (opt-in, agent-backed).

After a task's output is committed and verified, optionally review the change; if
the review is blocking (P0/P1), dispatch a fixer and re-review on the cumulative
diff, up to a cap. The review *judgment* is the one canonical review intelligence
(:mod:`review_agents` — diff-based, multi-reviewer, P0/P1/P2 → verdict); this
module only owns the fix loop, the iteration cap, and the resolved/unresolved
classification. Disabled by default; the zero-LLM core never enters this path.
"""
from __future__ import annotations

from dataclasses import dataclass

from inertia_forge.ignite_steps import DRIVER_TOOLS


@dataclass
class ReviewOutcome:
    resolved: bool
    iterations: int
    findings: str = ""


def _task_diff(root) -> str:
    from inertia_forge.gitcheck import _git
    return _git(root, "diff", "HEAD~1", "HEAD")


def _combined(result) -> str:
    return "\n\n".join(text for _, text in result.findings)


def _fix_prompt(task: dict, findings: str) -> str:
    return (
        f"A review of task {task.get('id', '')} found blocking issues. Fix ONLY "
        "the issues listed below, keeping changes minimal and the tests green.\n\n"
        f"Review findings:\n{findings}"
    )


def review_and_fix(task: dict, config, max_iterations: int = 3) -> ReviewOutcome:
    """Review the task's commit diff; fix-and-re-review until clean or capped."""
    from inertia_forge.agent import AgentSession
    from inertia_forge.review_agents import review_diff
    findings = ""
    for i in range(1, max_iterations + 1):
        result = review_diff(_task_diff(config.project_root), agents=["caliper"],
                             cli=config.agent, model=config.model,
                             root=config.project_root)
        if result.action != "request_changes":
            return ReviewOutcome(resolved=True, iterations=i, findings=_combined(result))
        findings = _combined(result)
        fixer = AgentSession(
            agent=config.agent, model=config.model, allowed_tools=DRIVER_TOOLS,
            permission_mode=config.permission_mode, working_dir=config.project_root)
        fixer.invoke(_fix_prompt(task, findings))
    return ReviewOutcome(resolved=False, iterations=max_iterations, findings=findings)
