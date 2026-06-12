"""Docstring coverage — how much of the public API is documented.

Counts public surface (module-level functions and classes, plus their public
methods), skipping underscore-private names, dunders, and test files, then
reports the fraction carrying a docstring and lists the ones that don't. `docs`
gates on ``--min`` (default 80%). Pure AST and deterministic — the documentation
analog of test coverage.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path


def _is_public(name: str) -> bool:
    return not name.startswith("_")


def _documentables(tree: ast.Module) -> list[tuple[str, ast.AST]]:
    """(qualified_name, node) for public top-level funcs/classes and methods."""
    out: list[tuple[str, ast.AST]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and _is_public(node.name):
            out.append((node.name, node))
            if isinstance(node, ast.ClassDef):
                for m in node.body:
                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_public(m.name):
                        out.append((f"{node.name}.{m.name}", m))
    return out


def analyze_file(path: str | Path) -> list[tuple[str, bool]]:
    """[(qualified_name, has_docstring)] for the public surface of a .py file."""
    p = Path(path)
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"), filename=str(p))
    except (OSError, SyntaxError):
        return []
    return [(name, ast.get_docstring(node) is not None) for name, node in _documentables(tree)]


def _collect(path: str) -> list[Path]:
    p = Path(path)
    files = p.rglob("*.py") if p.is_dir() else [p]
    return [f for f in files
            if "__pycache__" not in f.parts and "tests" not in f.parts
            and not f.name.startswith("test_")]


def run_docs(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    from inertia_forge.palette import paint
    parser = argparse.ArgumentParser(prog="inertia-forge docs")
    parser.add_argument("path", nargs="?", default=".", help="file or dir to scan")
    parser.add_argument("--min", type=float, default=80.0, help="minimum coverage %%")
    parser.add_argument("--list", action="store_true", help="list every undocumented symbol")
    args = parser.parse_args(argv)

    results = [(str(f), name, ok) for f in _collect(args.path) for name, ok in analyze_file(f)]
    if not results:
        print(f"{seal('ok')} no public symbols found")
        return 0
    missing = [(f, name) for f, name, ok in results if not ok]
    pct = 100.0 * (len(results) - len(missing)) / len(results)
    shown = missing if args.list else missing[:10]
    for f, name in shown:
        print(f"  {paint('undocumented', 'warn')} {name} ({f})")
    if len(missing) > len(shown):
        print(f"  {paint(f'... and {len(missing) - len(shown)} more', 'muted')}")
    role = "success" if pct >= args.min else "error"
    print(f"\n{seal('ok' if pct >= args.min else 'error')} docstring coverage "
          f"{paint(f'{pct:.1f}%', role, bold=True)} "
          f"({len(results) - len(missing)}/{len(results)}, min {args.min:g}%)")
    return 0 if pct >= args.min else 1
