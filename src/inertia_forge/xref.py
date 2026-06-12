"""Cross-reference integrity — dangling imports across the package.

After a refactor that renames or deletes a symbol, an ``import`` or a test that
still names the old symbol is silently broken until something runs it. This
finds them statically: every ``from <pkg>.<mod> import <name>`` whose ``<name>``
isn't defined, imported, or exported in ``<mod>``. A reference from a test file
is an *orphaned test*; any other is a *dangling import*. Both are high-confidence
real breakage — `xref` exits 1 on any. Deterministic AST analysis, no execution.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

from inertia_forge.deadcode import _is_test_file, _parse
from inertia_forge.importgraph import _find_package, _match, _modules


def _exported_names(tree: ast.Module) -> set[str]:
    """Names a module provides: top-level defs/classes/vars + import aliases + __all__."""
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update(a.asname or a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.Assign):
            names.update(t.id for t in node.targets if isinstance(t, ast.Name))
    return names


def dangling(root: str | Path) -> list[tuple[str, int, str, str, str]]:
    """[(file, line, target_module, name, category)] for each broken cross-reference."""
    pkg_dir = _find_package(str(root))
    pkg, mods = _modules(pkg_dir)
    modset = set(mods)
    symbols = {name: (_exported_names(t) if (t := _parse(p)) else set())
               for name, p in mods.items()}
    findings: list[tuple[str, int, str, str, str]] = []
    for name, path in mods.items():
        tree = _parse(path)
        if tree is None:
            continue
        category = "orphaned_test" if _is_test_file(path) else "dangling_import"
        for node in ast.walk(tree):
            if not (isinstance(node, ast.ImportFrom) and not node.level and node.module):
                continue
            target = _match(node.module, pkg, modset)
            if target is None or target not in symbols:
                continue
            for alias in node.names:
                nm = alias.name
                if nm == "*" or f"{target}.{nm}" in modset:  # wildcard or submodule import
                    continue
                if nm not in symbols[target]:
                    findings.append((str(path), node.lineno, target, nm, category))
    return findings


def run_xref(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    from inertia_forge.palette import paint
    p = argparse.ArgumentParser(prog="inertia-forge xref")
    p.add_argument("path", nargs="?", default=".", help="project or package dir")
    args = p.parse_args(argv)
    findings = dangling(args.path)
    if not findings:
        print(f"{seal('ok')} no dangling cross-references")
        return 0
    for file, line, target, name, category in findings:
        tag = "orphaned test" if category == "orphaned_test" else "dangling import"
        print(f"  {paint('[P1]', 'error')} {paint(name, 'error')} not in "
              f"{target} — {tag} ({file}:{line})")
    print(f"\n{seal('error')} {len(findings)} dangling cross-reference(s)")
    return 1
