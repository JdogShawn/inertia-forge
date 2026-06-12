"""Context freshness — flag stale continuity files before they mislead.

A context file (CLAUDE.md, the forge's context docs, the state ledger) older
than a threshold (default 7 days), or missing, is "stale" — the forge should
refresh it before trusting it. Deterministic: file mtime against an injectable
clock, so the check is testable and offline.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

STALE_DAYS = 7
_CONTEXT = (
    "CLAUDE.md",
    ".forge/context/project.md",
    ".forge/context/state.md",
    ".forge/context/workflow.md",
)


def is_stale(path: str | Path, days: int = STALE_DAYS, now: float | None = None) -> bool:
    """True if *path* is missing or older than *days* (boundary = fresh)."""
    p = Path(path)
    if not p.exists():
        return True
    clock = time.time() if now is None else now
    return (clock - p.stat().st_mtime) > days * 86400


def stale_files(root: Path, days: int = STALE_DAYS, now: float | None = None) -> list[str]:
    """The context files under *root* that are stale or missing."""
    return [rel for rel in _CONTEXT if is_stale(root / rel, days, now)]


def run_freshness(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge freshness")
    p.add_argument("--days", type=int, default=STALE_DAYS,
                   help=f"staleness threshold in days (default {STALE_DAYS})")
    args = p.parse_args(argv)
    root = Path(".")
    stale = stale_files(root, args.days)
    if not stale:
        print(f"{seal('ok')} context fresh (< {args.days}d)")
        return 0
    for rel in stale:
        tag = "missing" if not (root / rel).exists() else "stale"
        print(f"{seal('warn')} {tag}: {rel}")
    return 0
