"""Cyclomatic complexity — the branch-count metric arch's line check misses.

McCabe complexity = 1 + decision points (if/elif, for, while, except, each
boolean and/or, ternary, comprehension-if, and match cases). A long function can
be simple; a short one can be a maze — complexity measures the paths you must
test and reason about, which line count never sees. `complexity` ranks functions
and flags any over ``--max`` (default 10); exits 1 on an over-threshold function.
AST-based and deterministic; nested functions are scored on their own.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

DEFAULT_MAX = 10
_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _children_same_scope(node: ast.AST):
    """Walk descendants but stop at nested def/class boundaries."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, _DEFS):
            continue
        yield child
        yield from _children_same_scope(child)


def complexity_of(node: ast.AST) -> int:
    """McCabe complexity of one function body (excludes nested defs)."""
    score = 1
    for child in _children_same_scope(node):
        if isinstance(child, (ast.If, ast.For, ast.AsyncFor, ast.While,
                              ast.ExceptHandler, ast.IfExp, ast.comprehension)):
            score += 1
        elif isinstance(child, ast.BoolOp):
            score += len(child.values) - 1
        elif isinstance(child, ast.Match):
            score += len(child.cases)
    return score


def analyze_file(path: str | Path) -> list[tuple[str, int, int]]:
    """[(qualified_name, complexity, line)] for every function in a .py file."""
    p = Path(path)
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"), filename=str(p))
    except (OSError, SyntaxError):
        return []
    out: list[tuple[str, int, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append((node.name, complexity_of(node), node.lineno))
    return out


def _collect(path: str) -> list[Path]:
    p = Path(path)
    if p.is_dir():
        return [f for f in p.rglob("*.py") if "__pycache__" not in f.parts]
    return [p]


def run_complexity(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    from inertia_forge.palette import paint
    parser = argparse.ArgumentParser(prog="inertia-forge complexity")
    parser.add_argument("path", nargs="?", default=".", help="file or dir to scan")
    parser.add_argument("--max", type=int, default=DEFAULT_MAX, help="flag above this")
    parser.add_argument("--top", type=int, default=0, help="show only the N most complex")
    args = parser.parse_args(argv)

    scored = [(f, name, c, line) for f in _collect(args.path)
              for name, c, line in analyze_file(f)]
    scored.sort(key=lambda r: -r[2])
    over = [r for r in scored if r[2] > args.max]
    rows = scored[:args.top] if args.top else (over or scored[:10])
    for f, name, c, line in rows:
        role = "error" if c > args.max else ("warn" if c > args.max * 0.7 else "muted")
        print(f"  {paint(str(c).rjust(3), role)}  {name} ({f}:{line})")
    if over:
        print(f"\n{seal('error')} {len(over)} function(s) over complexity {args.max}")
        return 1
    print(f"\n{seal('ok')} all functions within complexity {args.max}")
    return 0
