"""Context compaction survival — snapshot / check / recover / cleanup.

When a long agent session gets compacted, working context is lost. The forge
survives it deterministically: `snapshot` freezes the current context pack to a
numbered file, `recover` re-emits the latest one for re-injection, `check`
reports whether a recoverable snapshot exists, and `cleanup` prunes old ones.
All plain file I/O — no clock, no network, git-diffable.
"""
from __future__ import annotations

import argparse
from pathlib import Path

SNAP_DIR = Path(".forge") / "snapshots"
PACK = Path(".forge") / "context_pack.md"


def _snapshots() -> list[Path]:
    if not SNAP_DIR.exists():
        return []
    return sorted(SNAP_DIR.glob("snapshot_*.md"))


def snapshot() -> Path:
    """Pack current context, then freeze it to the next numbered snapshot."""
    from inertia_forge.commands import run_pack
    run_pack([])  # writes .forge/context_pack.md
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    dest = SNAP_DIR / f"snapshot_{len(_snapshots()) + 1:03d}.md"
    dest.write_text(PACK.read_text(encoding="utf-8"), encoding="utf-8")
    return dest


def _h_snapshot(_a: argparse.Namespace) -> int:
    print(f"snapshot saved: {snapshot()}")
    return 0


def _h_check(_a: argparse.Namespace) -> int:
    snaps = _snapshots()
    if snaps:
        print(f"recoverable: {len(snaps)} snapshot(s), latest {snaps[-1].name}")
    elif PACK.exists():
        print("recoverable: context_pack.md (no snapshots yet)")
    else:
        print("no recoverable context — run `inertia-forge compaction snapshot`")
    return 0


def _h_recover(_a: argparse.Namespace) -> int:
    snaps = _snapshots()
    target = snaps[-1] if snaps else PACK
    if not target.exists():
        print("nothing to recover — take a snapshot first")
        return 1
    print(target.read_text(encoding="utf-8"))
    return 0


def _h_cleanup(a: argparse.Namespace) -> int:
    snaps = _snapshots()
    keep = max(0, a.keep)
    stale = snaps[:-keep] if keep else snaps
    for p in stale:
        p.unlink()
    print(f"removed {len(stale)} snapshot(s), kept {len(snaps) - len(stale)}")
    return 0


def run_compaction(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge compaction")
    sub = p.add_subparsers(dest="sub", required=True)
    sub.add_parser("snapshot", help="freeze current context to a snapshot").set_defaults(fn=_h_snapshot)
    sub.add_parser("check", help="report recoverable context").set_defaults(fn=_h_check)
    sub.add_parser("recover", help="print latest snapshot for re-injection").set_defaults(fn=_h_recover)
    cl = sub.add_parser("cleanup", help="prune old snapshots")
    cl.add_argument("--keep", type=int, default=5)
    cl.set_defaults(fn=_h_cleanup)
    args = p.parse_args(argv)
    return args.fn(args)
