"""CLI subcommand handlers for `python -m inertia_forge.skill_bridge`.

Kept separate from skill_bridge.py to honor the source-file line ceiling.
"""
from __future__ import annotations

import json as _json
import sys
from pathlib import Path

from inertia_forge.persisted_manifest import (
    MANIFEST_DIR,
    PersistedManifest,
    _session_filename,
)


def resolve_skill_for_target(target: str, wave_id: str = "") -> str | None:
    """Read the active session file for (target, wave_id) and return its skill."""
    active_path = MANIFEST_DIR / _session_filename(target, wave_id)
    if not active_path.exists():
        return None
    try:
        data = _json.loads(active_path.read_text(encoding="utf-8"))
    except (OSError, _json.JSONDecodeError):
        return None
    return data.get("skill")


def run_record_phase(phase: str, target: str, wave_id: str = "") -> int:
    """Canonical driver entry point. Loads session, records phase, auto-closes.

    Bundle D: when wave_id is provided, scopes to a specific parallel wave.
    """
    from inertia_forge.skill_bridge import ForgeSkillBridge

    skill = resolve_skill_for_target(target, wave_id)
    if not skill:
        wave_label = f" wave='{wave_id}'" if wave_id else ""
        print(
            f"ERROR: No active forge session for target '{target}'{wave_label}.",
            file=sys.stderr,
        )
        return 1

    bridge = ForgeSkillBridge(skill, target, wave_id=wave_id)
    result = bridge.record_phase(phase, Path(target))
    if not result.get("recorded"):
        print(
            f"Phase NOT recorded: {result.get('reason', 'unknown')}",
            file=sys.stderr,
        )
        return 1
    if result.get("blocked"):
        print(
            f"Phase '{phase}' BLOCKED: {result.get('p0')} P0 finding(s).",
            file=sys.stderr,
        )
        return 1
    print(
        f"Phase '{phase}' recorded "
        f"(p0={result.get('p0')}, p1={result.get('p1')}, "
        f"evidence={result.get('evidence_hash')}).",
    )
    if result.get("auto_closed"):
        print("FORGE SESSION AUTO-CLOSED — all blocking gates green.")
    return 0


def run_status() -> int:
    """Print the active session info, or report none."""
    if not PersistedManifest.session_exists():
        print("No active forge session.")
        return 1
    if MANIFEST_DIR.exists():
        for af in sorted(MANIFEST_DIR.glob("active*.json")):
            try:
                ad = _json.loads(af.read_text(encoding="utf-8"))
                sid = ad.get("session_id")
                if sid:
                    data = PersistedManifest.load(session_id=sid)
                    print(
                        f"Active session: {data.get('skill')} -> {data.get('target')}",
                    )
                    return 0
            except Exception:
                continue
    try:
        data = PersistedManifest.load()
        print(f"Active session: {data.get('skill')} -> {data.get('target')}")
        return 0
    except RuntimeError:
        print("Active session file found but no manifest on disk.")
        return 1


def cleanup_death_note_artifacts() -> None:
    """Delete death_note_active.json + stage summaries if stage >= 12.

    Extracted from skill_bridge.py to keep that module under the arch
    line ceiling. Pure side-effect function — safe to call multiple times.
    """
    dn_path = Path(".paircoder/enforcement/death_note_active.json")
    if not dn_path.exists():
        return
    try:
        data = _json.loads(dn_path.read_text(encoding="utf-8"))
        stage = data.get("stage", 0)
    except (OSError, _json.JSONDecodeError, ValueError):
        return
    if stage < 12:
        return
    dn_path.unlink(missing_ok=True)
    enforcement_dir = Path(".paircoder/enforcement")
    if enforcement_dir.exists():
        for summary in enforcement_dir.glob("death_note_stage_*_summary.md"):
            summary.unlink(missing_ok=True)


def run_close() -> int:
    """Manual close path — refuses when blocking gates remain incomplete."""
    from inertia_forge.completion_lock import count_incomplete_blocking_gates

    remaining = count_incomplete_blocking_gates()
    if remaining > 0:
        print(f"Cannot close: {remaining} blocking gate(s) remain incomplete.")
        return 1
    PersistedManifest.close_session()
    print("Session closed.")
    return 0
