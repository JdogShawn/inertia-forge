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


DEFAULT_THRESHOLD = 300  # only suggest splitting a file over this many lines


def suggest(path: str | Path, threshold: int = DEFAULT_THRESHOLD) -> list[tuple[str, str, list[str], int]]:
    """[(label, kind, [names], lines)] split components for an over-threshold file.

    Components are top-level CLASSES (each its own module) and cohesive function
    groups (3+ sharing a name prefix). A file at or under *threshold* lines is
    left alone — splitting a small file isn't worth it."""
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text, filename=str(p))
    except (OSError, SyntaxError):
        return []
    if len(text.splitlines()) <= threshold:
        return []
    components: list[tuple[str, str, list[str], int]] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            lines = (node.end_lineno or node.lineno) - node.lineno + 1
            components.append((node.name, "class", [node.name], lines))
    groups: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for name, start, end in _functions(tree):
        groups[_prefix(name)].append((name, end - start + 1))
    for label, members in groups.items():
        if len(members) >= 3:
            components.append((label, "functions", [m[0] for m in members],
                               sum(m[1] for m in members)))
    components.sort(key=lambda c: -c[3])
    return components


def _dest_module(stem: str, label: str, kind: str) -> str:
    if kind == "class":
        return f"{stem}_{label.lower()}.py"
    key = label.lstrip("_")
    return f"{stem}_{_DEST.get(key, key + '_group')}.py"


def run_suggest_split(argv: list[str]) -> int:
    from inertia_forge.glyphs import g, seal
    from inertia_forge.palette import paint
    p = argparse.ArgumentParser(prog="inertia-forge suggest-split")
    p.add_argument("path", help="an oversized source file")
    p.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD,
                   help=f"line count above which to suggest a split (default {DEFAULT_THRESHOLD})")
    args = p.parse_args(argv)
    sugg = suggest(args.path, args.threshold)
    if not sugg:
        print(f"{seal('ok')} no split suggested for {args.path} (under {args.threshold} lines)")
        return 0
    stem = Path(args.path).stem
    print(f"{seal('warn')} {args.path} — {len(sugg)} component(s) to extract:")
    arrow = g("arrow_l")
    for label, kind, names, lines in sugg:
        dest = paint(_dest_module(stem, label, kind), "accent")
        body = label if kind == "class" else ", ".join(names[:5]) + (" ..." if len(names) > 5 else "")
        print(f"  {dest}  {arrow} {kind} ({lines} lines): {body}")
    return 0
