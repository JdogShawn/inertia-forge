"""Retention — keep the forge's runtime files bounded on long-lived projects.

Deterministic pruning: trim the behavioral audit log to the last N entries and
drop cache blobs older than D days. `prune` runs them; both are safe and
idempotent, and use an injectable clock so the age check is testable.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

LOG = Path(".forge") / "behavioral_log.jsonl"
CACHE = Path(".forge") / "cache"


def prune_log(keep: int) -> int:
    """Trim the behavioral log to its last *keep* lines. Returns lines removed."""
    if not LOG.exists():
        return 0
    lines = [ln for ln in LOG.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(lines) <= keep:
        return 0
    removed = len(lines) - keep
    LOG.write_text("\n".join(lines[-keep:]) + "\n", encoding="utf-8")
    return removed


def prune_cache(days: int, now: float | None = None) -> int:
    """Delete cache blobs older than *days*. Returns blobs removed."""
    if not CACHE.is_dir():
        return 0
    clock = time.time() if now is None else now
    removed = 0
    for f in CACHE.glob("*"):
        if f.is_file() and (clock - f.stat().st_mtime) > days * 86400:
            f.unlink()
            removed += 1
    return removed


def run_prune(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge prune")
    p.add_argument("--keep", type=int, default=500,
                   help="behavioral-log entries to keep (default 500)")
    p.add_argument("--days", type=int, default=30,
                   help="max cache-blob age in days (default 30)")
    args = p.parse_args(argv)
    log_removed = prune_log(args.keep)
    cache_removed = prune_cache(args.days)
    print(f"{seal('ok')} pruned {log_removed} log entr(y/ies), "
          f"{cache_removed} cache blob(s)")
    return 0
