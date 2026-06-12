"""`ignite run` — drive an ingested backlog to done, autonomously.

The execution half of ignite: walk the task graph wave by wave (Piston
implements each task, gated per-task), then finalize — security-gate the branch
(Bastion), review it (Caliper/Sentinel/Lattice), and optionally open a PR. Pauses
at human-gated tasks to resumable state. LLM-agnostic: runs on whatever provider
is selected; `--dry-run` drives the whole loop with zero model calls.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from inertia_forge.ignite_engine import IgniteConfig, IgniteResult, IgniteRunner

_BRANCH_RE = re.compile(r"^[A-Za-z0-9/_.-]+$")


_PROTECTED = ("main", "master", "dev")


def _load_routing() -> dict | None:
    """Per-complexity model routing from `.forge/models.yaml` (`routing:` section)."""
    p = Path(".forge") / "models.yaml"
    if not p.exists():
        return None
    import yaml
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return None
    routing = data.get("routing")
    return routing if isinstance(routing, dict) else None


def _protected_branch(root: Path) -> str | None:
    """The current branch if it's protected (must not commit straight to it)."""
    from inertia_forge.gitcheck import _git
    branch = _git(root, "branch", "--show-current").strip()
    return branch if branch in _PROTECTED else None


def _checkout_branch(root: Path, branch: str) -> bool:
    """Create and checkout *branch*, falling back to a plain checkout if it
    already exists. Returns True on success. Name is validated for git safety."""
    if not branch or not _BRANCH_RE.match(branch) or branch.startswith("-"):
        from inertia_forge.glyphs import seal
        print(f"{seal('error')} invalid branch name {branch!r} — only A-Z a-z 0-9 "
              "/ _ . - allowed, must not start with '-'")
        return False
    create = subprocess.run(["git", "checkout", "-b", branch], cwd=str(root),
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", check=False)
    if create.returncode == 0:
        return True
    fallback = subprocess.run(["git", "checkout", branch], cwd=str(root),
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", check=False)
    return fallback.returncode == 0


def _exit_code(result: IgniteResult, fin: dict | None) -> int:
    if fin and fin.get("security_blocked"):
        return 2
    if result.failed or result.blocked or result.circuit_breaker_triggered:
        return 1
    return 0


def _print(result: IgniteResult, fin: dict | None) -> None:
    from inertia_forge.glyphs import g, seal
    bad = result.failed or result.blocked or result.circuit_breaker_triggered
    print(f"{seal('error' if bad else 'ok')} {len(result.completed)} done "
          f"({len(result.skipped)} already-satisfied) {g('dot')} "
          f"{len(result.failed)} failed {g('dot')} {len(result.blocked)} blocked "
          f"{g('dot')} {result.phases_completed} phase(s)")
    for tid in result.failed + result.blocked:
        print(f"  {seal('error')} {tid}: {result.failure_reasons.get(tid, '?')}")
    if not fin:
        return
    sec = fin.get("security") or {}
    if fin.get("security_blocked"):
        print(f"{seal('error')} security gate BLOCKED — P0 finding(s); PR withheld")
    elif sec.get("action") not in (None, "skipped"):
        print(f"{seal('ok')} security gate: {sec['action']}")
    review = fin.get("review")
    if review:
        print(f"{seal('ok')} review: {review['action']} ({', '.join(review['agents'])})")
    if fin.get("pr_url"):
        print(f"{seal('ok')} PR: {fin['pr_url']}")


def _branch_preflight(args: argparse.Namespace) -> int | None:
    """Checkout a requested feature branch and enforce protected-branch refusal.
    Returns an exit code to return immediately, or None to proceed."""
    from inertia_forge.glyphs import seal
    if args.branch and not args.dry_run and not _checkout_branch(Path("."), args.branch):
        print(f"{seal('error')} could not checkout branch '{args.branch}'")
        return 1
    if not args.dry_run and not args.force:
        protected = _protected_branch(Path("."))
        if protected:
            print(f"{seal('error')} refusing to run on protected branch "
                  f"'{protected}' — switch to a feature branch "
                  f"(git checkout -b <name>) or pass --force")
            return 2
    return None


def run_pipeline(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge ignite run")
    p.add_argument("--agent", default="claude", help="LLM provider (see `providers list`)")
    p.add_argument("--model", default=None)
    p.add_argument("--max-parallel", type=int, default=1)
    p.add_argument("--budget", type=int, default=None, help="token budget")
    p.add_argument("--dry-run", action="store_true",
                   help="drive the whole loop with ZERO model calls")
    p.add_argument("--review", action="store_true", help="review+fix each task")
    p.add_argument("--no-finalize", action="store_true",
                   help="skip the security gate + branch review after execution")
    p.add_argument("--pr", action="store_true", help="open a PR after a clean finalize")
    p.add_argument("--base", default="main", help="base branch for finalize/PR")
    p.add_argument("--branch", default="", help="create+checkout this feature branch first")
    p.add_argument("--force", action="store_true",
                   help="allow running on a protected branch (main/master/dev)")
    args = p.parse_args(argv)
    pre = _branch_preflight(args)
    if pre is not None:
        return pre

    cfg = IgniteConfig(
        project_root=Path("."), agent=args.agent, model=args.model,
        token_budget=args.budget, max_parallel=args.max_parallel,
        dry_run=args.dry_run, review=args.review, model_routing=_load_routing())
    result = IgniteRunner(cfg).run()

    if result.paused_task:
        from inertia_forge.glyphs import seal
        print(f"{seal('warn')} PAUSED at human-gated task {result.paused_task} — "
              f"resume: inertia-forge ignite resume {result.run_id}")
        return 0

    fin: dict | None = None
    if not args.dry_run and not args.no_finalize:
        from inertia_forge.ignite_finalize import finalize
        fin = finalize(result, Path("."), base=args.base, cli=args.agent,
                       model=args.model, do_pr=args.pr)
    _print(result, fin)
    return _exit_code(result, fin)
