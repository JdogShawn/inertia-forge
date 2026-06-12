"""Finalize an ignite run — gate, review, and (optionally) open a PR.

A security gate runs first and BLOCKS the rest if it finds a P0 (or errors —
fail-closed); otherwise the review agents judge the whole branch diff, an
optional PR is opened, and the outcome is recorded. Uses the forge's bundled
agents (Bastion gate, Caliper/Sentinel/Lattice review). Deterministic
orchestration around opt-in agent calls.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


def _pr_body(result) -> str:
    sections: list[str] = []
    if result.completed:
        sections.append("## Completed\n" + "\n".join(f"- {t}" for t in result.completed))
    if result.failed:
        sections.append("## Failed\n" + "\n".join(
            f"- {t}: {result.failure_reasons.get(t, '?')}" for t in result.failed))
    if getattr(result, "blocked", None):
        sections.append("## Blocked\n" + "\n".join(
            f"- {t}: {result.failure_reasons.get(t, '?')}" for t in result.blocked))
    return "\n\n".join(sections) or "(no tasks completed)"


def _detect_base(root: Path, preferred: str) -> str:
    """Honor *preferred* if it exists; else prefer dev, fall back to main."""
    from inertia_forge.gitcheck import _git
    branches = _git(root, "branch", "--list", "--format=%(refname:short)").split()
    if preferred in branches:
        return preferred
    return "dev" if "dev" in branches else "main"


def _pr_exists(root: Path, branch: str) -> bool:
    r = subprocess.run(
        ["gh", "pr", "list", "--head", branch, "--state", "open", "--limit", "1",
         "--json", "url", "-q", ".[0].url"], cwd=str(root), capture_output=True,
        text=True, encoding="utf-8", errors="replace", check=False)
    return r.returncode == 0 and bool(r.stdout.strip())


def create_pr(root: Path, result, base: str = "main", skip_if_exists: bool = False) -> str | None:
    """Push the branch and open a PR via gh. Returns the PR URL, or None."""
    if not result.completed:
        return None
    from inertia_forge.gitcheck import _git
    branch = _git(root, "branch", "--show-current").strip()
    if not branch:
        return None
    push = subprocess.run(["git", "push", "-u", "origin", branch], cwd=str(root),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", check=False)
    if push.returncode != 0:
        return None
    if skip_if_exists and _pr_exists(root, branch):
        return None
    title = f"ignite: {len(result.completed)} done, {len(result.failed)} failed"
    pr = subprocess.run(
        ["gh", "pr", "create", "--base", _detect_base(root, base), "--title", title,
         "--body", _pr_body(result)], cwd=str(root), capture_output=True,
        text=True, encoding="utf-8", errors="replace", check=False)
    return pr.stdout.strip() if pr.returncode == 0 else None


def _record(result, status: str) -> None:
    try:
        from inertia_forge.telemetry import record as trecord
        trecord("ignite", status, float(len(result.completed)),
                {"failed": len(result.failed), "phases": result.phases_completed})
    except Exception:
        pass


def finalize(result, root: Path, base: str = "main", cli: str = "claude",
             model: str | None = None, do_pr: bool = False,
             sec_dispatcher=None, review_dispatcher=None) -> dict:
    """Security-gate → review → optional PR. Returns a finalize result dict."""
    from inertia_forge.ignite_security import branch_diff, security_gate
    from inertia_forge.review_agents import review_diff
    out: dict = {"security": None, "review": None, "pr_url": None, "security_blocked": False}
    sec = security_gate(root, base, cli, model, dispatcher=sec_dispatcher)
    out["security"] = sec
    if sec["blocked"]:
        out["security_blocked"] = True
        _record(result, "security_blocked")
        return out
    review = review_diff(branch_diff(root, base), cli=cli, model=model,
                         root=root, dispatcher=review_dispatcher)
    out["review"] = {"action": review.action, "agents": review.agents, "errors": review.errors}
    if do_pr:
        out["pr_url"] = create_pr(root, result, base)
    _record(result, "partial" if result.failed else "completed")
    return out
