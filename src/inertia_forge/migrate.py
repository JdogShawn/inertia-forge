"""Schema migration framework — safe, versioned upgrades of `.forge/` state.

The forge stamps its on-disk schema version in `.forge/schema.json`. When a
storage format changes, register a migration; `migrate run` applies every
pending one in order and advances the version. This makes future format
changes safe instead of silently breaking old `.forge` dirs.

Deterministic: each migration is a pure transform of on-disk state, no LLM.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA_VERSION = 1
SCHEMA_FILE = Path(".forge") / "schema.json"

# (target_version, description, fn) — fn applies the transform for that step.
_MIGRATIONS: list[tuple[int, str, callable]] = []


def migration(target: int, description: str):
    def deco(fn):
        _MIGRATIONS.append((target, description, fn))
        return fn
    return deco


def current_version() -> int:
    if not SCHEMA_FILE.exists():
        return 0
    try:
        return int(json.loads(SCHEMA_FILE.read_text(encoding="utf-8")).get("version", 0))
    except (json.JSONDecodeError, ValueError, TypeError):
        return 0


def _set_version(n: int) -> None:
    SCHEMA_FILE.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_FILE.write_text(json.dumps({"version": n}, indent=2) + "\n", encoding="utf-8")


def pending() -> list[tuple[int, str, callable]]:
    cur = current_version()
    return sorted((m for m in _MIGRATIONS if m[0] > cur), key=lambda m: m[0])


def run() -> list[str]:
    applied = []
    for target, desc, fn in pending():
        fn()
        _set_version(target)
        applied.append(f"v{target}: {desc}")
    return applied


# ── Migrations ───────────────────────────────────────────────────────
@migration(1, "establish .forge schema versioning")
def _m1() -> None:
    # No data transform needed — this baselines existing .forge dirs at v1 so
    # future migrations have a known starting point.
    pass


def run_migrate(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge migrate")
    sub = p.add_subparsers(dest="sub", required=True)
    sub.add_parser("status")
    sub.add_parser("run")
    args = p.parse_args(argv)
    if args.sub == "run":
        applied = run()
        if not applied:
            print(f"already at latest schema (v{SCHEMA_VERSION})")
            return 0
        for a in applied:
            print(f"  applied {a}")
        print(f"migrated to v{current_version()}")
        return 0
    cur = current_version()
    print(f"current schema: v{cur}  |  latest: v{SCHEMA_VERSION}")
    pend = pending()
    if pend:
        for target, desc, _ in pend:
            print(f"  pending v{target}: {desc}")
    else:
        print("  up to date")
    return 0
