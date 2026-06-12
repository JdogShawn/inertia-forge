"""CLI for `inertia-forge engage` — run the autonomous loop, resume a paused
run, or list paused runs. Kept out of engage.py so the engine stays import-light.

  engage [run] [--dry-run] [--agent claude] [--model M] [--max-parallel N]
               [--permission-mode auto] [--budget TOKENS] [--no-commit]
  engage resume <run-id> [same flags]
  engage runs
"""
from __future__ import annotations

import argparse
from pathlib import Path

from inertia_forge.engage import EngageConfig, EngageResult, EngageRunner


def _add_run_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--agent", default="claude", help="coding-agent CLI to dispatch to")
    p.add_argument("--model", default=None)
    p.add_argument("--dry-run", action="store_true",
                   help="drive the loop with ZERO LLM calls (no dispatch, no commit)")
    p.add_argument("--max-parallel", type=int, default=1)
    p.add_argument("--permission-mode", default="auto")
    p.add_argument("--budget", type=int, default=None, help="token budget for the run")
    p.add_argument("--no-commit", action="store_true",
                   help="do not commit or output-verify (dispatch only)")
    p.add_argument("--no-targeted-tests", action="store_true",
                   help="run the full suite, not just tests for changed files")
    p.add_argument("--review", action="store_true",
                   help="dispatch a reviewer (and fixer loop) after each task")
    p.add_argument("--max-review-iterations", type=int, default=3)


def _config(args: argparse.Namespace) -> EngageConfig:
    return EngageConfig(
        project_root=Path("."), agent=args.agent, model=args.model,
        permission_mode=args.permission_mode, token_budget=args.budget,
        max_parallel=args.max_parallel, dry_run=args.dry_run,
        commit=not (args.no_commit or args.dry_run),
        targeted_tests=not args.no_targeted_tests,
        review=args.review, max_review_iterations=args.max_review_iterations,
    )


def _print_result(res: EngageResult) -> None:
    from inertia_forge.glyphs import g, seal
    if res.paused_task:
        print(f"{seal('warn')} PAUSED at human-gated task {res.paused_task} "
              f"{g('dot')} resume with: inertia-forge ignite resume {res.run_id}")
    head = "error" if (res.failed or res.circuit_breaker_triggered) else "ok"
    print(f"{seal(head)} {len(res.completed)} done "
          f"({len(res.skipped)} already-satisfied) {g('dot')} "
          f"{len(res.failed)} failed {g('dot')} {res.phases_completed} phase(s)")
    for tid in res.failed:
        print(f"  {seal('error')} {tid}: {res.failure_reasons.get(tid, '?')}")
    if res.circuit_breaker_triggered:
        from inertia_forge.engage_recovery import recovery_guidance
        print(f"{seal('error')} circuit breaker tripped — failure ratio too high")
        for line in recovery_guidance(res.failure_reasons):
            print(f"  {line}")


def _exit_code(res: EngageResult) -> int:
    return 1 if (res.failed or res.circuit_breaker_triggered) else 0


def _do_run(args: argparse.Namespace) -> int:
    res = EngageRunner(_config(args)).run()
    _print_result(res)
    return _exit_code(res)


def _do_resume(args: argparse.Namespace) -> int:
    from inertia_forge.engage_runstate import load_run_state
    from inertia_forge.glyphs import seal
    try:
        state = load_run_state(Path("."), args.run_id)
    except (FileNotFoundError, ValueError) as exc:
        print(f"{seal('error')} {exc}")
        return 1
    cfg = _config(args)
    cfg.max_parallel = state.max_parallel
    res = EngageRunner(cfg).run()
    _print_result(res)
    return _exit_code(res)


def _do_runs(_args: argparse.Namespace) -> int:
    from inertia_forge.engage_runstate import list_runs
    runs = list_runs(Path("."))
    if not runs:
        print("(no paused engage runs)")
        return 0
    for rid in runs:
        print(f"  {rid}")
    return 0


def run_engage(argv: list[str]) -> int:
    sub = argv[0] if argv else "run"
    if sub not in ("run", "resume", "runs"):
        argv = ["run", *argv]  # default subcommand
    p = argparse.ArgumentParser(prog="inertia-forge engage")
    subs = p.add_subparsers(dest="sub")
    r = subs.add_parser("run", help="run the autonomous loop")
    _add_run_flags(r)
    rs = subs.add_parser("resume", help="resume a paused run")
    rs.add_argument("run_id")
    _add_run_flags(rs)
    subs.add_parser("runs", help="list paused runs")
    args = p.parse_args(argv)
    return {"run": _do_run, "resume": _do_resume, "runs": _do_runs}[args.sub](args)
