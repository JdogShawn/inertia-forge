"""Forge Completion Lock — mechanical enforcement of blocking gates.

Provides helpers that shell hooks call to determine whether a forge
session has incomplete blocking gates. Used by:
  - prevent-death-note-stop.sh (Stop hook)
  - enforce-bash-gate.sh (PreToolUse hook)
  - inject-death-note.sh (UserPromptSubmit hook)

Session-scoped: reads active_*.json to find session IDs, then reads
manifest_{session_id}.json for each. Falls back to legacy manifest.json.

Fail-open: any exception returns 0 / None so hooks do not crash Claude.
"""
from __future__ import annotations

import json
from pathlib import Path

MANIFEST_PATH = Path(".forge") / "manifest.json"
MANIFEST_DIR = Path(".forge")


#: Evidence-hash prefixes that indicate the phase did NOT run real work.
#: A phase whose evidence_hash starts with any of these strings counts as
#: NOT COMPLETED — the sentinel keeps the gate blocking until real work
#: produces a real evidence hash.
#:
#: This closes the manual-release backdoor: writing a phase record with
#: `evidence_hash: "manual_release_*"` used to clear the gate even though
#: no methodology ran. Now those phases are rejected and a real run is
#: required to satisfy the gate.
#:
#: Drivers and tools that legitimately need to mark a phase complete
#: without running it (e.g. one-shot session releases approved by the
#: user) should record an explicit override marker in the session's
#: `released_by` field at the top level of the manifest — that is
#: audited separately and is NOT this list.
_BYPASS_EVIDENCE_PREFIXES: tuple[str, ...] = (
    "manual_release",  # any manual_release_* variant
    "pending",         # placeholder phases written before real work
    "stub",            # stub markers
    "bypass",          # explicit bypass markers
    "placeholder",     # placeholder markers
    "TODO",            # TODO markers in evidence
)


def _phase_is_bypassed(phase_record: object) -> bool:
    """True if the phase record carries a bypass-marker evidence hash."""
    if not isinstance(phase_record, dict):
        return False
    evidence = phase_record.get("evidence_hash", "")
    if not isinstance(evidence, str):
        return False
    return any(evidence.startswith(prefix) for prefix in _BYPASS_EVIDENCE_PREFIXES)


def _count_gates_for_manifest(data: dict) -> int:
    """Count incomplete blocking gates for a single manifest's data.

    A phase counts as COMPLETED only when:
      1. Its name is present in the manifest's `phases` dict, AND
      2. Its evidence_hash is NOT a bypass marker (see _BYPASS_EVIDENCE_PREFIXES).

    A top-level `released_by` field on the manifest is honored as an
    explicit user-authorized override and clears all remaining gates.
    """
    skill = data.get("skill", "")
    if not skill:
        return 0

    from inertia_forge.skill_registry import (
        get_required_steps,
        validate_skill_name,
    )

    if not validate_skill_name(skill):
        return 0

    # Explicit user-authorized override at manifest top-level.
    # Format: {"released_by": "<user>", "released_reason": "<reason>", ...}
    if data.get("released_by"):
        return 0

    blocking = get_required_steps(skill)
    phases = data.get("phases", {})
    if not isinstance(phases, dict):
        phases = {}

    remaining = []
    for step in blocking:
        record = phases.get(step)
        if record is None:
            remaining.append(step)
            continue
        if _phase_is_bypassed(record):
            remaining.append(step)
            continue
        # A recorded phase whose verifier found P0 (blocking) findings is
        # NOT complete — the gate stays open until the P0s are resolved.
        # Aligns the gate count with _maybe_auto_close (refuses on p0 != 0).
        if isinstance(record, dict) and record.get("p0", 0) > 0:
            remaining.append(step)
    return len(remaining)


def _active_file_is_fresh(active_data: dict) -> bool:
    """Bundle B (F5): True if the session was started within SESSION_MAX_AGE.

    Stale sessions stop contributing to the gate count so the Stop hook
    isn't blocked by orphans from days ago. Fail-open: malformed
    timestamps are treated as fresh (better to over-block once than
    silently drop a real session).
    """
    from datetime import datetime, timezone

    from inertia_forge.persisted_manifest import SESSION_MAX_AGE

    try:
        started = datetime.fromisoformat(active_data.get("started_at", ""))
    except (ValueError, TypeError):
        return True
    return (datetime.now(timezone.utc) - started) <= SESSION_MAX_AGE


def _active_file_owned_by(active_data: dict, claude_session_id: str) -> bool:
    """Bundle B (F4 + F7): True if this active session belongs to the
    given Claude Code session_id.

    When the caller passes a claude_session_id, only sessions whose
    active_*.json carries a matching ``claude_session_id`` field count.
    Sessions without an owner field are treated as belonging to nobody —
    they don't block this Claude's Stop hook.

    When the caller passes "" (no filter), every session counts (legacy
    behavior preserved for hooks not yet updated).
    """
    if not claude_session_id:
        return True
    return active_data.get("claude_session_id") == claude_session_id


def count_gates_for_session(target: str, wave_id: str = "") -> int:
    """Bundle D: count incomplete blocking gates for ONE specific session.

    Used by _maybe_auto_close so a wave's auto-close only depends on
    THAT wave's gates, not on every active session in the .forge dir.
    Returns 0 if the session doesn't exist (fail-open).
    """
    try:
        from inertia_forge.persisted_manifest import (
            MANIFEST_DIR,
            _session_filename,
        )

        active_path = MANIFEST_DIR / _session_filename(target, wave_id)
        if not active_path.exists():
            return 0
        active_data = json.loads(active_path.read_text(encoding="utf-8"))
        if not _active_file_is_fresh(active_data):
            return 0
        sid = active_data.get("session_id")
        if not sid:
            return 0
        manifest_path = MANIFEST_DIR / f"manifest_{sid}.json"
        if not manifest_path.exists():
            return 0
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return _count_gates_for_manifest(data)
    except Exception:
        return 0


def _count_one_active_file(
    active_file: Path,
    claude_session_id: str,
    seen_sessions: set[str],
) -> int:
    """Process a single active_*.json: filters + manifest read + count.

    Returns 0 on any read/parse error (fail-open) or if the session is
    stale (F5) or not owned by claude_session_id (F4).
    """
    try:
        active_data = json.loads(active_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0
    session_id = active_data.get("session_id")
    if not session_id:
        return 0
    if not _active_file_is_fresh(active_data):
        return 0
    if not _active_file_owned_by(active_data, claude_session_id):
        return 0
    seen_sessions.add(session_id)
    manifest_path = MANIFEST_DIR / f"manifest_{session_id}.json"
    if not manifest_path.exists():
        return 0
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0
    return _count_gates_for_manifest(data)


def count_incomplete_blocking_gates(claude_session_id: str = "") -> int:
    """Return the number of blocking gates not yet completed.

    Filters by freshness (F5: <24h) and owning Claude session (F4: when
    claude_session_id is provided). Returns 0 on any error (fail-open).
    """
    try:
        total = 0
        seen_sessions: set[str] = set()

        if MANIFEST_DIR.exists():
            for active_file in sorted(MANIFEST_DIR.glob("active*.json")):
                total += _count_one_active_file(
                    active_file, claude_session_id, seen_sessions,
                )

        # Legacy manifest.json fallback (no owner field — only counts when
        # the caller didn't request owner-filtering).
        if MANIFEST_PATH.exists() and not claude_session_id:
            data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
            legacy_sid = data.get("session_id", "")
            if legacy_sid not in seen_sessions:
                total += _count_gates_for_manifest(data)

        return total

    except Exception:
        return 0


def _scan_owned_active(claude_session_id: str) -> tuple[bool, str | None]:
    """Find the first fresh, owned active session. Returns (has_active, skill).

    Owner-filtered (F4) + freshness-filtered (F5): a session owned by a
    different Claude tab, or older than SESSION_MAX_AGE, is skipped.
    """
    if not MANIFEST_DIR.exists():
        return False, None
    for active_file in sorted(MANIFEST_DIR.glob("active*.json")):
        try:
            active_data = json.loads(active_file.read_text(encoding="utf-8"))
            session_id = active_data.get("session_id")
            if not session_id:
                continue
            if not _active_file_is_fresh(active_data):
                continue
            if not _active_file_owned_by(active_data, claude_session_id):
                continue
            manifest_path = MANIFEST_DIR / f"manifest_{session_id}.json"
            skill = None
            if manifest_path.exists():
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                skill = data.get("skill", "unknown")
            return True, skill
        except (json.JSONDecodeError, OSError):
            continue
    return False, None


def get_forge_status(claude_session_id: str = "") -> str | None:
    """Return a human-readable status string, or None if no session.

    Owner-filtered (F4) and freshness-filtered (F5), symmetric with
    count_incomplete_blocking_gates: when ``claude_session_id`` is given,
    only sessions owned by THIS Claude tab are reported — a fresh tab is
    never told it is "inside" a foreign tab's session. When "" is passed,
    every session counts (legacy behavior).
    """
    try:
        has_active, first_skill = _scan_owned_active(claude_session_id)

        # Legacy fallback (no owner field — only when caller didn't filter).
        if not has_active and not claude_session_id and MANIFEST_PATH.exists():
            data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
            first_skill = data.get("skill", "unknown")
            has_active = True

        if not has_active:
            return None

        remaining = count_incomplete_blocking_gates(claude_session_id)
        skill_name = first_skill or "unknown"
        return f"Skill: {skill_name} | {remaining} blocking gate(s) remaining"

    except Exception:
        return None
