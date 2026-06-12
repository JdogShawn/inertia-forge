"""Backlog validation — check a markdown backlog before igniting it.

Validates structure WITHOUT mutating the store: a valid-typed plan, at least one
task, well-formed task ids, every task with acceptance criteria and a
verification command, and no duplicate ids. `backlog validate <file>` reports
issues and exits 1 on any error; `ignite --check` pre-flights with the same rules.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from inertia_forge import tasks as t
from inertia_forge.ignite import parse_backlog


def _find_cycle(tasks: list[dict]) -> list[str] | None:
    """One dependency cycle as an id path over the parsed tasks, or None."""
    ids = {task["id"] for task in tasks}
    edges = {task["id"]: [d for d in task.get("depends_on", []) if d in ids] for task in tasks}
    color: dict[str, int] = {tid: 0 for tid in edges}  # 0 white 1 gray 2 black
    stack: list[str] = []

    def visit(tid: str) -> list[str] | None:
        color[tid] = 1
        stack.append(tid)
        for d in edges[tid]:
            if color[d] == 1:
                return stack[stack.index(d):] + [d]
            if color[d] == 0 and (cyc := visit(d)):
                return cyc
        color[tid] = 2
        stack.pop()
        return None

    for tid in edges:
        if color[tid] == 0 and (cyc := visit(tid)):
            return cyc
    return None


def validate(text: str) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for a backlog's text. Pure, deterministic."""
    plan, tasks = parse_backlog(text)
    errors: list[str] = []
    warnings: list[str] = []
    if plan["type"] not in t.VALID_PLAN_TYPES:
        errors.append(f"plan type {plan['type']!r} invalid (use {', '.join(t.VALID_PLAN_TYPES)})")
    if not tasks:
        errors.append("no tasks found (expected '## T<sprint>.<seq>: title' headings)")
    seen: set[str] = set()
    for task in tasks:
        tid = task["id"]
        if tid in seen:
            errors.append(f"{tid}: duplicate task id")
        seen.add(tid)
        if not t.TASK_ID_RE.match(tid):
            errors.append(f"{tid}: id must match T<sprint>.<seq>")
        if not task["ac"]:
            errors.append(f"{tid}: no acceptance criteria (add '- [ ] ...' lines)")
        if not task["verify"]:
            errors.append(f"{tid}: no 'verify:' command (TDD requires one)")
        if task["complexity"] <= 0:
            warnings.append(f"{tid}: no complexity estimate")
        for dep in task.get("depends_on", []):
            if dep not in seen and dep not in {x["id"] for x in tasks}:
                errors.append(f"{tid}: depends on unknown task {dep!r}")
    cyc = _find_cycle(tasks)
    if cyc:
        errors.append(f"dependency cycle: {' → '.join(cyc)}")
    return errors, warnings


def run_backlog(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge backlog")
    sub = p.add_subparsers(dest="sub", required=True)
    v = sub.add_parser("validate", help="check a backlog .md before igniting")
    v.add_argument("file")
    args = p.parse_args(argv)
    path = Path(args.file)
    if not path.is_file():
        print(f"backlog not found: {path}")
        return 1
    errors, warnings = validate(path.read_text(encoding="utf-8"))
    for w in warnings:
        print(f"{seal('warn')} {w}")
    for e in errors:
        print(f"{seal('error')} {e}")
    if errors:
        return 1
    print(f"{seal('ok')} backlog valid ({len(warnings)} warning(s))")
    return 0
