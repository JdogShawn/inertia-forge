"""Pre-dispatch acceptance-criteria satisfaction check.

Before dispatching a task to an agent, ask: is its acceptance criteria already
satisfied on disk? Extract testable claims from the AC text — file paths and
code symbols in `backticks` — and check them deterministically (file existence;
a Python-native, cross-platform symbol scan, no unix ``grep``).

Conservative by design: declare ALREADY_SATISFIED only when at least one file
claim exists AND every claim checks out. Pure-symbol tasks fall back to
UNCERTAIN → dispatch (generic names like ``run`` over-match), which is safer
than skipping unimplemented work.
"""
from __future__ import annotations

import re
from enum import Enum
from pathlib import Path

_FILE_RE = re.compile(r"`([A-Za-z0-9_/.\-]+\.[A-Za-z0-9]+)`")
_SYMBOL_RE = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*(?:\(\))?)`")
_CODE_EXT = {".py", ".ts", ".js", ".tsx", ".jsx", ".yaml", ".yml", ".json",
             ".toml", ".md", ".html", ".css", ".go", ".rs", ".java", ".rb"}
_EXCLUDED = (".forge/", ".venv/", ".claude/", ".git/", "node_modules/", "__pycache__/")
_SCAN_DIRS_SKIP = {".git", ".venv", "node_modules", "__pycache__", ".forge", "dist", "build"}


class CheckResult(Enum):
    NEEDS_WORK = "needs_work"
    ALREADY_SATISFIED = "already_satisfied"
    UNCERTAIN = "uncertain"


def _claims(text: str) -> list[tuple[str, str]]:
    """(kind, value) claims from one AC line: ("file", path) / ("symbol", name)."""
    out: list[tuple[str, str]] = []
    for m in _FILE_RE.finditer(text):
        path = m.group(1)
        ext = "." + path.rsplit(".", 1)[-1] if "." in path else ""
        if "/" in path and ext in _CODE_EXT:
            out.append(("file", path))
    for m in _SYMBOL_RE.finditer(text):
        sym = m.group(1).rstrip("()")
        if "/" not in sym and "." not in sym:
            out.append(("symbol", sym))
    return out


def _file_exists(root: Path, rel: str) -> bool | None:
    """True/False, or None when the path is an excluded runtime artifact."""
    if any(rel.startswith(p) for p in _EXCLUDED):
        return None
    return (root / rel).exists()


def _symbol_in_tree(root: Path, symbol: str) -> bool:
    """Whole-word symbol scan over code files (Python-native, cross-platform)."""
    pat = re.compile(r"\b" + re.escape(symbol) + r"\b")
    for path in root.rglob("*.py"):
        if any(part in _SCAN_DIRS_SKIP for part in path.parts):
            continue
        try:
            if pat.search(path.read_text(encoding="utf-8", errors="replace")):
                return True
        except OSError:
            continue
    return False


def pre_dispatch_check(ac_texts: list[str], project_root: Path) -> CheckResult:
    """Is the task's AC already satisfied on disk? See module docstring."""
    claims: list[tuple[str, str]] = []
    for text in ac_texts:
        claims.extend(_claims(text))
    if not claims:
        return CheckResult.UNCERTAIN
    files_ok = 0
    for kind, value in claims:
        if kind == "file":
            exists = _file_exists(project_root, value)
            if exists is None:
                continue
            if not exists:
                return CheckResult.NEEDS_WORK
            files_ok += 1
        elif kind == "symbol":
            if not _symbol_in_tree(project_root, value):
                return CheckResult.NEEDS_WORK
    if files_ok == 0:
        return CheckResult.UNCERTAIN
    return CheckResult.ALREADY_SATISFIED
