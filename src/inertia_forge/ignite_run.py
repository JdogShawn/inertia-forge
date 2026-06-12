"""`ignite run` — drive an ingested backlog to done, autonomously.

The execution half of ignite: walk the task graph wave by wave (Piston
implements each task, gated per-task), then finalize — security-gate the branch
(Bastion), review it (Caliper/Sentinel/Lattice), and optionally open a PR. Pauses
at human-gated tasks to resumable state. LLM-agnostic: runs on whatever provider
is selected; `--dry-run` drives the whole loop with zero model calls.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from inertia_forge.ignite_engine import IgniteConfig, IgniteResult, IgniteRunner


def _exit_code(result: IgniteResult, fin: dict | None) -> int:
    if fin and fin.get("security_blocked"):
        return 2
    if result.failed or result.circuit_breaker_triggered:
        return 1
    return 0


def _print(result: IgniteResult, fin: dict | None) -> None:
    from inertia_forge.glyphs import g, seal
    head = "error" if (result.failed or result.circuit_breaker_triggered) else "ok"
    print(f"{seal(head)} {len(result.completed)} done "
          f"({len(result.skipped)} already-satisfied) {g('dot')} "
          f"{len(result.failed)} failed {g('dot')} {result.phases_completed} phase(s)")
    for tid in result.failed:
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
    args = p.parse_args(argv)

    cfg = IgniteConfig(
        project_root=Path("."), agent=args.agent, model=args.model,
        token_budget=args.budget, max_parallel=args.max_parallel,
        dry_run=args.dry_run, review=args.review)
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
