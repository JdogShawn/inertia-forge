"""Dead-code sweep — deterministic unused-import detection (AST).

Lighter than a full linter: per module, bind the names an import introduces,
then check whether each is referenced anywhere in that module. Unreferenced
bindings are reported (and `--fix` removes the simple single-name ones).

Conservative by design — it skips `__future__`, anything named in `__all__`,
and lines carrying `# noqa`, so it doesn't fight re-exports.
"""
from __future__ import annotations

import ast
from pathlib import Path


def _imported_names(tree: ast.AST) -> list[tuple[str, int, str]]:
    """Return (bound_name, lineno, raw) for every import binding."""
    out: list[tuple[str, int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                bound = (a.asname or a.name).split(".")[0]
                out.append((bound, node.lineno, f"import {a.name}"))
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                continue
            for a in node.names:
                if a.name == "*":
                    continue
                out.append((a.asname or a.name, node.lineno, f"from {node.module} import {a.name}"))
    return out


def _used_names(tree: ast.AST) -> set[str]:
    used: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            base = node
            while isinstance(base, ast.Attribute):
                base = base.value
            if isinstance(base, ast.Name):
                used.add(base.id)
    return used


def find_unused_imports(filepath: Path) -> list[dict]:
    """Report unused imports in one file as P2 findings."""
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except (OSError, UnicodeDecodeError, SyntaxError):
        return []
    lines = content.splitlines()
    exported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
        ):
            exported = {ast.literal_eval(e) for e in getattr(node.value, "elts", [])
                        if isinstance(e, ast.Constant)}
    used = _used_names(tree)
    findings: list[dict] = []
    for bound, lineno, raw in _imported_names(tree):
        line = lines[lineno - 1] if 0 < lineno <= len(lines) else ""
        if bound in used or bound in exported or "# noqa" in line:
            continue
        findings.append({"severity": "P2", "rule": "unused_import",
                         "file": str(filepath), "line": lineno,
                         "message": f"{filepath.name}:{lineno}: unused import ({raw})"})
    return findings


def sweep_path(path: Path) -> list[dict]:
    """Sweep a file or directory tree for unused imports."""
    if path.is_file():
        return find_unused_imports(path)
    findings: list[dict] = []
    for f in sorted(path.rglob("*.py")):
        if "__pycache__" not in str(f):
            findings += find_unused_imports(f)
    return findings


def _fix_file(filepath: Path, linenos: list[int]) -> int:
    """Remove flagged SINGLE-binding import lines (no comma/paren). Conservative."""
    try:
        lines = filepath.read_text(encoding="utf-8").splitlines(keepends=True)
    except OSError:
        return 0
    removed = 0
    for ln in sorted(linenos, reverse=True):
        if 0 < ln <= len(lines):
            s = lines[ln - 1].strip()
            if "," not in s and "(" not in s and (s.startswith("import ") or s.startswith("from ")):
                del lines[ln - 1]
                removed += 1
    if removed:
        filepath.write_text("".join(lines), encoding="utf-8")
    return removed


def run_sweep(argv: list[str]) -> int:
    """inertia-forge sweep [path] [--fix] — report (or remove) unused imports."""
    import argparse

    parser = argparse.ArgumentParser(prog="inertia-forge sweep")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--fix", action="store_true", help="remove simple unused imports")
    args = parser.parse_args(argv)
    target = Path(args.path)
    findings = sweep_path(target)
    if args.fix and findings:
        by_file: dict[str, list[int]] = {}
        for f in findings:
            by_file.setdefault(f["file"], []).append(f["line"])
        total = sum(_fix_file(Path(fp), lns) for fp, lns in by_file.items())
        print(f"removed {total} unused import line(s)")
        findings = sweep_path(target)
    if not findings:
        print("OK: no unused imports")
        return 0
    for f in findings:
        print(f"  [{f['severity']}] {f['message']}")
    print(f"\n{len(findings)} unused import(s)")
    return 1
