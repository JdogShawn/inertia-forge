"""Plan-level estimation — project a session-token cost from complexity.

`plan estimate` multiplies the remaining tasks' total complexity by a
tokens-per-point rate and compares it to a session threshold, so you can see
*before* starting whether a plan fits one session. Deterministic — the same
inputs always give the same projection.
"""
from __future__ import annotations

import argparse

from inertia_forge import tasks as t

DEFAULT_TPP = 1500          # tokens per complexity point
DEFAULT_THRESHOLD = 120_000  # comfortable single-session ceiling


def estimate_plan(tokens_per_point: int = DEFAULT_TPP) -> dict:
    """Project remaining-work token cost from the task store. Pure."""
    pending = [x for x in t.list_tasks() if x["status"] != "done"]
    points = sum(x.get("complexity", 0) for x in pending)
    return {"tasks": len(pending), "points": points,
            "tokens": int(points * tokens_per_point)}


def run_plan(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge plan")
    sub = p.add_subparsers(dest="sub", required=True)
    es = sub.add_parser("estimate", help="project token cost from complexity")
    es.add_argument("--tokens-per-point", type=int, default=DEFAULT_TPP)
    es.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    args = p.parse_args(argv)

    plan = t.get_plan()
    est = estimate_plan(args.tokens_per_point)
    if plan:
        print(f"plan: {plan['type']} — {plan['title']}")
    print(f"remaining: {est['tasks']} task(s) · {est['points']:g} complexity points")
    print(f"projected: ~{est['tokens']} tokens (@ {args.tokens_per_point}/pt)")
    over = est["tokens"] > args.threshold
    print(f"{seal('error' if over else 'ok')} "
          f"{'OVER' if over else 'within'} session threshold {args.threshold}")
    return 1 if over else 0
