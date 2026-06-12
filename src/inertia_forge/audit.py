"""Cross-repo audit — shared-contract impact + sibling health. Deterministic.

When two repos share code, a change in one can break the other. This extracts
the public symbols THIS repo exports, finds which ones a SIBLING repo consumes
(the shared contracts at risk), and runs the analyzer on the sibling. All static
— AST + regex, no LLM, no network.
"""
from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path


def exported_symbols(repo: Path) -> set[str]:
    """Public top-level function/class names defined across a repo's .py files."""
    out: set[str] = set()
    for py in repo.rglob("*.py"):
        if "__pycache__" in str(py):
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, OSError):
            continue
        for node in tree.body:
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                    and not node.name.startswith("_")):
                out.add(node.name)
    return out


def consumers(repo: Path, symbols: set[str]) -> dict[str, list[str]]:
    """For each symbol, the sibling files that reference it (the shared contracts)."""
    pats = {s: re.compile(rf"\b{re.escape(s)}\b") for s in symbols}
    hits: dict[str, list[str]] = {}
    for py in repo.rglob("*.py"):
        if "__pycache__" in str(py):
            continue
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for s, pat in pats.items():
            if pat.search(text):
                hits.setdefault(s, []).append(py.name)
    return hits


def _health(repo: Path) -> dict:
    from inertia_forge.independent_analyzer import analyze_directory
    findings = analyze_directory(repo)
    return {"p0": sum(1 for f in findings if f["severity"] == "P0"), "findings": len(findings)}


def audit(sibling: Path, src: Path) -> dict:
    exported = exported_symbols(src)
    return {
        "exported": len(exported),
        "shared": consumers(sibling, exported),
        "health": _health(sibling),
    }


def run_audit(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge audit")
    p.add_argument("sibling", help="path to the sibling repository")
    p.add_argument("--src", default="src" if Path("src").is_dir() else ".",
                   help="this repo's source dir (default: src)")
    args = p.parse_args(argv)
    sibling = Path(args.sibling)
    if not sibling.is_dir():
        print(f"sibling repo not found: {sibling}")
        return 1
    a = audit(sibling, Path(args.src))
    h = a["health"]
    print(f"Cross-repo audit: {sibling}")
    print(f"  sibling health: {h['p0']} P0, {h['findings']} finding(s)")
    print(f"  symbols this repo exports: {a['exported']}")
    if a["shared"]:
        print(f"  shared contracts (changing these may break the sibling):")
        for sym, files in sorted(a["shared"].items()):
            print(f"    {sym}: used in {', '.join(sorted(set(files))[:4])}")
    else:
        print("  no shared contracts detected")
    return 1 if h["p0"] else 0
