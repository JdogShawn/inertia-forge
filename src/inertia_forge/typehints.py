"""Type-hint coverage — how much of the public API is annotated.

A public function or method counts as fully typed when every parameter (self /
cls excluded) carries an annotation AND the return is annotated. `types` reports
the fraction fully typed across the public surface and lists the gaps, gating on
``--min`` (default 80%). Pure AST and deterministic — the typing analog of
docstring and test coverage.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

from inertia_forge.docstrings import _collect, _is_public


def _is_typed(node: ast.FunctionDef | ast.AsyncFunctionDef, is_method: bool) -> bool:
    a = node.args
    params = list(a.posonlyargs) + list(a.args) + list(a.kwonlyargs)
    if is_method and params and params[0].arg in ("self", "cls"):
        params = params[1:]
    if a.vararg:
        params.append(a.vararg)
    if a.kwarg:
        params.append(a.kwarg)
    return all(p.annotation is not None for p in params) and node.returns is not None


def _typeables(tree: ast.Module) -> list[tuple[str, bool]]:
    """(qualified_name, is_fully_typed) for public top-level funcs + methods."""
    out: list[tuple[str, bool]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_public(node.name):
            out.append((node.name, _is_typed(node, is_method=False)))
        elif isinstance(node, ast.ClassDef) and _is_public(node.name):
            for m in node.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_public(m.name):
                    out.append((f"{node.name}.{m.name}", _is_typed(m, is_method=True)))
    return out


def analyze_file(path: str | Path) -> list[tuple[str, bool]]:
    """[(qualified_name, fully_typed)] for the public functions of a .py file."""
    p = Path(path)
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"), filename=str(p))
    except (OSError, SyntaxError):
        return []
    return _typeables(tree)


def run_types(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    from inertia_forge.palette import paint
    parser = argparse.ArgumentParser(prog="inertia-forge types")
    parser.add_argument("path", nargs="?", default=".", help="file or dir to scan")
    parser.add_argument("--min", type=float, default=80.0, help="minimum coverage %%")
    parser.add_argument("--list", action="store_true", help="list every untyped function")
    args = parser.parse_args(argv)

    results = [(str(f), name, ok) for f in _collect(args.path) for name, ok in analyze_file(f)]
    if not results:
        print(f"{seal('ok')} no public functions found")
        return 0
    missing = [(f, name) for f, name, ok in results if not ok]
    pct = 100.0 * (len(results) - len(missing)) / len(results)
    shown = missing if args.list else missing[:10]
    for f, name in shown:
        print(f"  {paint('untyped', 'warn')} {name} ({f})")
    if len(missing) > len(shown):
        print(f"  {paint(f'... and {len(missing) - len(shown)} more', 'muted')}")
    role = "success" if pct >= args.min else "error"
    print(f"\n{seal('ok' if pct >= args.min else 'error')} type-hint coverage "
          f"{paint(f'{pct:.1f}%', role, bold=True)} "
          f"({len(results) - len(missing)}/{len(results)}, min {args.min:g}%)")
    return 0 if pct >= args.min else 1
