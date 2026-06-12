"""Project-wide dead-symbol detection — defined-but-never-referenced code.

Deeper than per-file unused imports (`sweep`): AST-collect every top-level
function and class across a tree, then every identifier referenced anywhere
(plain names, attribute accesses, ``from x import y`` aliases, and ``__all__``
entries). A symbol whose name appears nowhere outside its own definition — and
isn't a CLI entry-point, a test, a dunder, or underscore-private — is reported
as likely-dead.

Conservative by design: dynamic dispatch (getattr, registries, string lookup)
can hide a real use, so findings are advisory P2 — `dead-code` exits 0 unless
``--strict`` is given. Pairs with `sweep` (imports) for a full cleanliness pass.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

# Names we never flag: CLI entry-points, tests, dunders, underscore-private.
_KEEP_PREFIX = ("test_", "run_", "_")
_KEEP_EXACT = {"main"}


def _py_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]


def _is_test_file(p: Path) -> bool:
    return ("tests" in p.parts or p.name.startswith("test_")
            or p.name == "conftest.py")


def _parse(f: Path) -> ast.Module | None:
    try:
        return ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
    except (OSError, SyntaxError):
        return None


def definitions(files: list[Path]) -> dict[str, tuple[Path, int]]:
    """{name: (file, line)} for every top-level def/class across *files*."""
    defs: dict[str, tuple[Path, int]] = {}
    for f in files:
        tree = _parse(f)
        if tree is None:
            continue
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defs.setdefault(node.name, (f, node.lineno))
    return defs


def _all_strings(node: ast.AST) -> set[str]:
    if isinstance(node, (ast.List, ast.Tuple)):
        return {e.value for e in node.elts
                if isinstance(e, ast.Constant) and isinstance(e.value, str)}
    return set()


def referenced_names(files: list[Path]) -> set[str]:
    """Every identifier referenced anywhere — names, attrs, import aliases, __all__."""
    used: set[str] = set()
    for f in files:
        tree = _parse(f)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used.add(node.id)
            elif isinstance(node, ast.Attribute):
                used.add(node.attr)
            elif isinstance(node, ast.ImportFrom):
                used.update(a.name for a in node.names)
            elif isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
                used.update(_all_strings(node.value))
    return used


def _kept(name: str) -> bool:
    return (name.startswith(_KEEP_PREFIX) or name in _KEEP_EXACT
            or (name.startswith("__") and name.endswith("__")))


def find_dead(root: Path) -> list[tuple[str, Path, int]]:
    """(name, file, line) for each non-test top-level symbol never referenced.

    Definitions come only from non-test files (dead test helpers are noise);
    references are gathered from EVERY file, so a symbol exercised solely by the
    test suite still counts as used.
    """
    files = _py_files(root)
    defs = definitions([f for f in files if not _is_test_file(f)])
    used = referenced_names(files)
    return [(name, f, line) for name, (f, line) in sorted(defs.items())
            if not _kept(name) and name not in used]


def run_dead_code(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    from inertia_forge.palette import paint
    p = argparse.ArgumentParser(prog="inertia-forge dead-code")
    p.add_argument("path", nargs="?", default=".", help="tree to scan")
    p.add_argument("--strict", action="store_true", help="exit 1 if any dead symbols")
    args = p.parse_args(argv)
    dead = find_dead(Path(args.path))
    if not dead:
        print(f"{seal('ok')} no dead symbols found")
        return 0
    for name, f, line in dead:
        print(f"  {paint('[P2]', 'muted')} {paint(name, 'warn')} "
              f"defined but never referenced ({f}:{line})")
    print(f"\n{seal('warn')} {len(dead)} likely-dead symbol(s) "
          f"{paint('(advisory — dynamic uses can hide real references)', 'muted')}")
    return 1 if args.strict else 0
