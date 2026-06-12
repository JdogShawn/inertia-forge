"""Per-task review-and-fix loop (opt-in, agent-backed).

After a task's output is committed and verified, optionally dispatch a reviewer
over the change; if it returns a blocking verdict, dispatch a fixer and
re-review, up to a cap. The loop, the iteration cap, and the resolved/unresolved
classification are all deterministic — only the review and fix *judgments* go to
an agent. Disabled by default; the zero-LLM core never enters this path.

The reviewer is asked to end its reply with ``VERDICT: clean`` or
``VERDICT: blocking``; anything else is read as clean (never fail a task on an
unparseable review).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from inertia_forge.engage_steps import DRIVER_TOOLS

REVIEWER_TOOLS = ["Read", "Grep", "Glob", "Bash"]  # read-only review
_BLOCKING_RE = re.compile(r"VERDICT:\s*blocking", re.IGNORECASE)


@dataclass
class ReviewOutcome:
    resolved: bool
    iterations: int
    findings: str = ""


def _review_prompt(task: dict) -> str:
    return (
        f"Review the changes that implement task {task.get('id', '')}: "
        f"{task.get('title', '')}.\n"
        "Check correctness, the acceptance criteria, tests, and obvious quality "
        "issues. List any blocking findings concisely.\n"
        "End your reply with exactly one line: 'VERDICT: clean' if the change is "
        "good to keep, or 'VERDICT: blocking' if it must be fixed first."
    )


def _fix_prompt(task: dict, findings: str) -> str:
    return (
        f"A review of task {task.get('id', '')} found blocking issues. Fix them, "
        "keeping changes minimal and the tests green.\n\nReview findings:\n"
        f"{findings}"
    )


def _is_blocking(review_text: str) -> bool:
    return bool(_BLOCKING_RE.search(review_text or ""))


def review_and_fix(task: dict, config, max_iterations: int = 3) -> ReviewOutcome:
    """Review the task's change; fix-and-re-review until clean or capped."""
    from inertia_forge.agent import AgentSession
    findings = ""
    for i in range(1, max_iterations + 1):
        reviewer = AgentSession(
            agent=config.agent, model=config.model, allowed_tools=REVIEWER_TOOLS,
            permission_mode="plan", working_dir=config.project_root)
        resp = reviewer.invoke(_review_prompt(task))
        if resp.is_error or not _is_blocking(resp.result):
            return ReviewOutcome(resolved=True, iterations=i, findings=resp.result)
        findings = resp.result
        fixer = AgentSession(
            agent=config.agent, model=config.model, allowed_tools=DRIVER_TOOLS,
            permission_mode=config.permission_mode, working_dir=config.project_root)
        fixer.invoke(_fix_prompt(task, findings))
    return ReviewOutcome(resolved=False, iterations=max_iterations, findings=findings)
