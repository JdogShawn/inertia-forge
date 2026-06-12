"""Deterministic code review — the leftover smells a structural check misses.

Flags what should never ship: real debug leftovers (``breakpoint()``,
``pdb.set_trace()``, ``import pdb``, ``console.log``, ``debugger``), TODO /
FIXME / HACK / XXX markers, and hardcoded network endpoints (localhost,
127.0.0.1, 0.0.0.0). Python debug calls are found via AST so strings/comments
don't false-positive; markers and endpoints via line scan across any language.

Reviews the git-changed set by default, or an explicit file/dir. Debug leftovers
are P1; markers and endpoints are P2. `review` exits 1 on any P1. (Bare
``print`` is intentionally NOT flagged — a CLI prints by design.)
"""
from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

_MARKERS = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")
_ENDPOINTS = re.compile(r"\b(localhost|127\.0\.0\.1|0\.0\.0\.0)\b")
_DEBUG_TEXT = re.compile(r"(console\.log|\bdebugger\b)")
_TEXT_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".yaml", ".yml",
             ".sh", ".txt", ".json", ".cfg", ".ini", ".toml"}


def _py_debug(path: Path) -> list[tuple[int, str]]:
    """AST hits for breakpoint() / pdb.set_trace() / import pdb in a .py file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError):
        return []
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "breakpoint"):
            out.append((node.lineno, "breakpoint() call"))
        elif isinstance(node, ast.Attribute) and node.attr == "set_trace":
            out.append((node.lineno, "pdb.set_trace()"))
        elif isinstance(node, ast.Import) and any(a.name == "pdb" for a in node.names):
            out.append((node.lineno, "import pdb"))
        elif isinstance(node, ast.ImportFrom) and node.module == "pdb":
            out.append((node.lineno, "import pdb"))
    return out


def review_file(path: str | Path) -> list[dict]:
    """Every review finding in a single file."""
    p = Path(path)
    findings: list[dict] = []
    if p.suffix == ".py":
        findings += [{"severity": "P1", "message": f"{p}:{line} debug leftover — {msg}"}
                     for line, msg in _py_debug(p)]
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    is_py = p.suffix == ".py"
    for i, line in enumerate(text.splitlines(), 1):
        # console.log / debugger are JS-isms; on Python they're only ever in
        # strings or docs (AST already covers real Python debug leftovers).
        if not is_py and (m := _DEBUG_TEXT.search(line)):
            findings.append({"severity": "P1", "message": f"{p}:{i} debug leftover — {m.group(0)}"})
        if m := _MARKERS.search(line):
            findings.append({"severity": "P2", "message": f"{p}:{i} {m.group(0)} marker"})
        if m := _ENDPOINTS.search(line):
            findings.append({"severity": "P2", "message": f"{p}:{i} hardcoded endpoint {m.group(0)}"})
    return findings


def _collect(path: str | None, since: str) -> list[Path]:
    if path:
        p = Path(path)
        if p.is_dir():
            return [f for f in p.rglob("*")
                    if f.is_file() and f.suffix in _TEXT_EXT and "__pycache__" not in f.parts]
        return [p]
    from inertia_forge.targeted import git_changed
    return [Path(f) for f in git_changed(Path("."), since)
            if Path(f).is_file() and Path(f).suffix in _TEXT_EXT]


def run_review(argv: list[str]) -> int:
    from inertia_forge.glyphs import g, seal
    from inertia_forge.palette import paint
    p = argparse.ArgumentParser(prog="inertia-forge review")
    p.add_argument("path", nargs="?", help="file/dir to review (default: git-changed)")
    p.add_argument("--since", default="HEAD", help="git ref to diff against")
    args = p.parse_args(argv)
    findings: list[dict] = []
    for f in _collect(args.path, args.since):
        findings += review_file(f)
    if not findings:
        print(f"{seal('ok')} no review findings")
        return 0
    role = {"P1": "error", "P2": "muted"}
    for sev in ("P1", "P2"):
        for f in (x for x in findings if x["severity"] == sev):
            print(f"  {paint(f'[{sev}]', role[sev])} {f['message']}")
    p1 = sum(1 for f in findings if f["severity"] == "P1")
    p2 = len(findings) - p1
    print(f"\n{seal('error' if p1 else 'warn')} {p1} P1 {g('dot')} {p2} P2")
    return 1 if p1 else 0
