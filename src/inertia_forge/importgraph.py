"""Module import graph — circular-import detection across a package.

Builds the internal import graph (each module → the package modules it imports)
and finds cycles. It distinguishes HARD edges (module-level imports, which run at
import time) from SOFT edges (imports inside a function, deferred until called).
A cycle made only of hard edges is a real import-time hazard (P1); a cycle that
passes through a soft edge is broken at import time and reported as advisory —
exactly the pattern the forge uses on purpose (a bottom import + a lazy import).
AST-based and deterministic.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path


def _find_package(path: str) -> Path:
    p = Path(path)
    if (p / "__init__.py").exists():
        return p
    for cand in sorted(p.glob("*/__init__.py")) + sorted(p.glob("src/*/__init__.py")):
        return cand.parent
    return p


def _modules(pkg_dir: Path) -> tuple[str, dict[str, Path]]:
    parent = pkg_dir.parent
    mods: dict[str, Path] = {}
    for f in pkg_dir.rglob("*.py"):
        if "__pycache__" in f.parts:
            continue
        parts = list(f.relative_to(parent).with_suffix("").parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        mods[".".join(parts)] = f
    return pkg_dir.name, mods


def _match(name: str, pkg: str, modset: set[str]) -> str | None:
    if not (name == pkg or name.startswith(pkg + ".")):
        return None
    parts = name.split(".")
    for i in range(len(parts), 0, -1):
        cand = ".".join(parts[:i])
        if cand in modset:
            return cand
    return None


def imports_of(path: Path, pkg: str, modset: set[str]) -> tuple[set[str], set[str]]:
    """(hard, soft) internal modules imported by *path* — soft = inside a function."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError):
        return set(), set()
    soft_ids: set[int] = set()
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            soft_ids.update(id(n) for n in ast.walk(fn)
                            if isinstance(n, (ast.Import, ast.ImportFrom)))
    hard: set[str] = set()
    soft: set[str] = set()
    for node in ast.walk(tree):
        targets: set[str] = set()
        if isinstance(node, ast.Import):
            targets = {m for a in node.names if (m := _match(a.name, pkg, modset))}
        elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
            # `from pkg import submodule` depends on the SUBMODULE (resolved on
            # its own), not on pkg/__init__. Only when the imported names are
            # plain attributes does the edge fall to the module they live in.
            subs = {m for a in node.names
                    if (m := _match(f"{node.module}.{a.name}", pkg, modset))}
            if subs:
                targets = subs
            elif m := _match(node.module, pkg, modset):
                targets = {m}
        else:
            continue
        (soft if id(node) in soft_ids else hard).update(targets)
    return hard, soft


def build_graph(pkg_dir: Path, soft: bool = False) -> dict[str, set[str]]:
    pkg, mods = _modules(pkg_dir)
    graph: dict[str, set[str]] = {}
    for name, path in mods.items():
        h, s = imports_of(path, pkg, set(mods))
        edges = (h | s) if soft else h
        graph[name] = {e for e in edges if e != name}
    return graph


def find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    color = {n: 0 for n in graph}
    stack: list[str] = []

    def visit(n: str) -> list[str] | None:
        color[n] = 1
        stack.append(n)
        for m in sorted(graph.get(n, ())):
            if color.get(m, 0) == 1:
                return stack[stack.index(m):] + [m]
            if color.get(m, 0) == 0 and (c := visit(m)):
                return c
        color[n] = 2
        stack.pop()
        return None

    for n in sorted(graph):
        if color[n] == 0 and (c := visit(n)):
            return c
    return None


def run_imports(argv: list[str]) -> int:
    from inertia_forge.glyphs import g, seal
    p = argparse.ArgumentParser(prog="inertia-forge imports")
    p.add_argument("path", nargs="?", default=".", help="project or package dir")
    args = p.parse_args(argv)
    pkg_dir = _find_package(args.path)
    hard = build_graph(pkg_dir, soft=False)
    hard_cycle = find_cycle(hard)
    fan_in: dict[str, int] = {}
    for deps in hard.values():
        for d in deps:
            fan_in[d] = fan_in.get(d, 0) + 1
    top = sorted(fan_in.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    print(f"{len(hard)} module(s) {g('dot')} most depended-on: "
          + ", ".join(f"{m.split('.')[-1]}({n})" for m, n in top))
    if hard_cycle:
        arrow = g("arrow_r")
        print(f"{seal('error')} import-time cycle: {(' ' + arrow + ' ').join(hard_cycle)}")
        return 1
    soft_cycle = find_cycle(build_graph(pkg_dir, soft=True))
    if soft_cycle:
        print(f"{seal('warn')} soft cycle (lazy-resolved, safe): "
              f"{(' ' + g('arrow_r') + ' ').join(soft_cycle)}")
    print(f"{seal('ok')} no import-time cycles")
    return 0
