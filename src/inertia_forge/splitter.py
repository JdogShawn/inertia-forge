"""Module split adviser — when a file is too big, recommend how to break it up.

`arch` flags an oversized file (too many lines or functions); this proposes a
concrete split. It clusters top-level functions by shared name prefix (``run_*``,
``_check_*``, ``_cmd_*``, ``handle_*``, …), and for each cohesive group of three
or more suggests extracting it into a sibling module — with the line count the
move would shed. Deterministic AST analysis; advisory, never a gate.
"""
from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from pathlib import Path

# prefix (underscore-stripped) → destination module suffix
_DEST = {"check": "checks", "run": "commands", "cmd": "commands", "handle": "handlers",
         "verify": "verifiers", "vet": "checks", "build": "builders", "parse": "parsers"}


def _functions(tree: ast.Module) -> list[tuple[str, int, int]]:
    return [(n.name, n.lineno, n.end_lineno or n.lineno)
            for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _prefix(name: str) -> str:
    parts = name.lstrip("_").split("_")
    return ("_" if name.startswith("_") else "") + parts[0]


def suggest(path: str | Path) -> list[tuple[str, list[str], int]]:
    """[(prefix, [names], lines_shed)] split candidates, largest group first."""
    p = Path(path)
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"), filename=str(p))
    except (OSError, SyntaxError):
        return []
    funcs = _functions(tree)
    if len(funcs) < 8:  # small files aren't worth splitting
        return []
    groups: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for name, start, end in funcs:
        groups[_prefix(name)].append((name, end - start + 1))
    out = [(label, [m[0] for m in members], sum(m[1] for m in members))
           for label, members in groups.items() if len(members) >= 3]
    out.sort(key=lambda s: (-len(s[1]), -s[2]))
    return out


def _dest_module(stem: str, prefix: str) -> str:
    key = prefix.lstrip("_")
    return f"{stem}_{_DEST.get(key, key + '_group')}.py"


def run_suggest_split(argv: list[str]) -> int:
    from inertia_forge.glyphs import g, seal
    from inertia_forge.palette import paint
    p = argparse.ArgumentParser(prog="inertia-forge suggest-split")
    p.add_argument("path", help="an oversized source file")
    args = p.parse_args(argv)
    sugg = suggest(args.path)
    if not sugg:
        print(f"{seal('ok')} no split suggested for {args.path}")
        return 0
    stem = Path(args.path).stem
    print(f"{seal('warn')} {args.path} — {len(sugg)} extraction candidate(s):")
    arrow = g("arrow_l")
    for label, names, lines in sugg:
        dest = paint(_dest_module(stem, label), "accent")
        shown = ", ".join(names[:6]) + (" ..." if len(names) > 6 else "")
        print(f"  {dest}  {arrow} {len(names)} fn(s), {lines} lines: {shown}")
    return 0
