"""PersistedManifest — session-scoped .forge/manifest_{session_id}.json.

Battle Scar #14 fix: manifest persists to DISK after every phase.
Integrity hash (SHA-256) detects post-hoc tampering.
Session-specific salt prevents hash precomputation (Bypass #17 fix).

T73.11: Scoped session locks — per-target .forge/active_{hash}.json files
allow parallel forge sessions on different directories.

Session-scoped manifests: each session writes to manifest_{session_id}.json
so multiple Claude sessions do not overwrite each other's state. The active
session file contains the session_id linking to its manifest.
"""
from __future__ import annotations

import glob as _glob_mod
import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

MANIFEST_DIR = Path(".forge")
MANIFEST_PATH = MANIFEST_DIR / "manifest.json"
SESSION_PATH = MANIFEST_DIR / "active.json"
SESSION_MAX_AGE = timedelta(hours=24)


def _session_filename(target: str | None = None, wave_id: str = "") -> str:
    """Compute the session filename for a given target (Bundle D wave-aware).

    Returns 'active.json' for None (legacy global), or
    'active_{hash8}.json' where hash8 = SHA-256[:8] of the resolved
    target path — optionally suffixed with `|wave={wave_id}` when a
    wave_id is provided.

    Backward compat: when wave_id is empty (default), the hash input
    is byte-identical to the pre-Bundle-D behavior, so all existing
    sessions, tests, and on-disk files keep their filenames.
    Setting a wave_id produces a distinct hash so multiple parallel
    waves on the same target each get their own active file.
    """
    if target is None:
        return "active.json"
    normalized = str(Path(target).resolve())
    if wave_id:
        normalized = f"{normalized}|wave={wave_id}"
    h = hashlib.sha256(normalized.encode()).hexdigest()[:8]
    return f"active_{h}.json"


class PersistedManifest:
    """Manifest that persists to disk and detects tampering."""

    def __init__(self, skill_name: str, target: str,
                 claude_session_id: str = "", wave_id: str = "") -> None:
        self._skill = skill_name
        self._target = target
        self._session_id = str(uuid.uuid4())[:8]
        self._salt = str(uuid.uuid4())  # Session-specific, prevents precomputation
        self._started_at = datetime.now(timezone.utc).isoformat()
        self._phases: dict[str, dict] = {}
        # Bundle B (F4): owning Claude Code session_id; embedded in the
        # active file so other tabs' Stop hooks can filter past it.
        self._claude_session_id = claude_session_id
        # Bundle D: wave_id namespace; lets N parallel waves run on the
        # same target without colliding on the active filename.
        self._wave_id = wave_id

    def record_phase(self, phase: str, findings: list[dict],
                     evidence_hash: str) -> None:
        """Record a phase with computed findings and evidence hash."""
        p0 = sum(1 for f in findings if f.get("severity") == "P0")
        p1 = sum(1 for f in findings if f.get("severity") == "P1")
        p2 = sum(1 for f in findings if f.get("severity") == "P2")

        self._phases[phase] = {
            "p0": p0, "p1": p1, "p2": p2,
            "finding_count": len(findings),
            "findings": findings[:20],
            "evidence_hash": evidence_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "computed": True,
        }
        self.save()

    def _manifest_path(self) -> Path:
        """Return session-scoped manifest path: manifest_{session_id}.json."""
        return MANIFEST_DIR / f"manifest_{self._session_id}.json"

    def save(self) -> None:
        """Persist to disk with integrity hash (session-scoped)."""
        MANIFEST_DIR.mkdir(exist_ok=True)
        data = {
            "session_id": self._session_id,
            "skill": self._skill,
            "target": self._target,
            "started_at": self._started_at,
            "phases": self._phases,
            "integrity_hash": self._compute_integrity(),
        }
        self._manifest_path().write_text(
            json.dumps(data, indent=2), encoding="utf-8",
        )

    @classmethod
    def load(cls, session_id: str | None = None) -> dict:
        """Load and verify integrity. Raises on tamper.

        Args:
            session_id: If provided, load manifest_{session_id}.json.
                        If None, fall back to legacy manifest.json.
        """
        if session_id is not None:
            path = MANIFEST_DIR / f"manifest_{session_id}.json"
        else:
            path = MANIFEST_PATH  # legacy fallback
        if not path.exists():
            raise RuntimeError("No manifest on disk. Start a forge session first.")
        data = json.loads(path.read_text(encoding="utf-8"))
        stored_hash = data.get("integrity_hash", "")
        # Recompute from phase data
        phase_json = json.dumps(data.get("phases", {}), sort_keys=True)
        expected = hashlib.sha256(phase_json.encode()).hexdigest()
        if stored_hash != expected:
            raise RuntimeError(
                "MANIFEST TAMPERED. Integrity hash mismatch. "
                "The manifest was modified outside the forge system."
            )
        return data

    @classmethod
    def load_for_session(cls, session_id: str) -> dict:
        """Load a specific session's manifest by session_id.

        Convenience wrapper around load(session_id=...).
        Raises RuntimeError if the session manifest does not exist.
        """
        return cls.load(session_id=session_id)

    def is_zero_debt(self) -> bool:
        """Check persisted manifest — all phases must have p0=0 and p1=0."""
        for phase_data in self._phases.values():
            if phase_data.get("p0", 0) > 0 or phase_data.get("p1", 0) > 0:
                return False
        return len(self._phases) > 0

    def check_evidence_freshness(self, phase: str,
                                  max_age_seconds: int = 300) -> bool:
        """Evidence must be fresh — stale evidence rejected (Bypass #8)."""
        pd = self._phases.get(phase)
        if not pd:
            return False
        recorded = datetime.fromisoformat(pd["timestamp"])
        age = (datetime.now(timezone.utc) - recorded).total_seconds()
        return age <= max_age_seconds

    def check_consistency(self) -> list[str]:
        """Detect file changes between phases (Bypass #9)."""
        issues: list[str] = []
        prev_hash = None
        prev_name = None
        for name, data in self._phases.items():
            h = data.get("evidence_hash")
            if prev_hash and h != prev_hash:
                issues.append(f"Files changed between {prev_name} and {name}")
            prev_hash = h
            prev_name = name
        return issues

    def _compute_integrity(self) -> str:
        phase_json = json.dumps(self._phases, sort_keys=True)
        return hashlib.sha256(phase_json.encode()).hexdigest()

    def create_session_file(self) -> None:
        """Create scoped session file marking an active session.

        Uses .forge/active_{hash}.json for target-scoped locks (T73.11).
        Embeds the owning claude_session_id (Bundle B) when set so the
        Stop hook in other Claude tabs can filter past it.
        Embeds wave_id (Bundle D) when set so parallel waves on the
        same target don't collide on the active filename.
        """
        MANIFEST_DIR.mkdir(exist_ok=True)
        fname = _session_filename(self._target, self._wave_id)
        session_path = MANIFEST_DIR / fname
        payload: dict = {
            "session_id": self._session_id,
            "skill": self._skill,
            "target": self._target,
            "started_at": self._started_at,
        }
        if self._claude_session_id:
            payload["claude_session_id"] = self._claude_session_id
        if self._wave_id:
            payload["wave_id"] = self._wave_id
        session_path.write_text(
            json.dumps(payload, indent=2), encoding="utf-8",
        )

    @staticmethod
    def _check_session_file(path: Path) -> bool:
        """Check if a single session file is valid and non-stale.

        Returns True if the file represents an active (non-expired) session.
        Fail-safe: malformed files are treated as active.
        """
        if not path.exists():
            return False
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            started = datetime.fromisoformat(data.get("started_at", ""))
            if datetime.now(timezone.utc) - started > SESSION_MAX_AGE:
                from inertia_forge.bypass_prevention import log_behavioral_event

                sid = data.get("session_id", "unknown")
                log_behavioral_event(
                    "session_expired",
                    f"Stale session {sid} expired after 24h",
                )
                return False
        except (json.JSONDecodeError, ValueError, KeyError, TypeError):
            pass  # Can't parse — fail-safe: treat as active
        return True

    @staticmethod
    def session_exists(
        target: str | None = ..., wave_id: str = "",
        claude_session_id: str = "",
    ) -> bool:
        """Check if a forge session is active.

        Args:
            target: If a string, check only the scoped file for that target.
                    If None (or omitted), check for ANY active session file
                    (glob .forge/active*.json), including legacy active.json.
            wave_id: Bundle D — when scoped (target is a string), this also
                     scopes by wave so parallel waves on the same target
                     are checked independently. Ignored for any-session
                     glob mode.
            claude_session_id: F4 owner-aware activation. When provided and
                     the scoped session is owned by a DIFFERENT Claude tab,
                     returns False so the auto-forge hook starts/adopts the
                     target's single slot — this is what clears an abandoned
                     cross-tab zombie that would otherwise suppress every new
                     tab's auto-activation for up to 24h. When omitted
                     (default), behavior is byte-identical to before.

        The sentinel default (...) distinguishes "not passed" from "passed as None".
        Both omitted and explicit None trigger the any-session glob.
        """
        if target is not ...:
            # Scoped check for a specific target (and optional wave).
            fname = _session_filename(target, wave_id)
            path = MANIFEST_DIR / fname
            if not PersistedManifest._check_session_file(path):
                return False
            if claude_session_id:
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    return True  # fail-safe: unreadable counts as existing
                owner = data.get("claude_session_id", "")
                # A fresh session owned by another tab must not block THIS
                # tab. Unowned (legacy) sessions stay blocking — can't tell.
                if owner and owner != claude_session_id:
                    return False
            return True

        # No target: check for ANY active session (scoped or legacy)
        pattern = str(MANIFEST_DIR / "active*.json")
        candidates = _glob_mod.glob(pattern)
        for candidate in candidates:
            if PersistedManifest._check_session_file(Path(candidate)):
                return True
        return False

    @staticmethod
    def close_session(target: str | None = ..., wave_id: str = "") -> None:
        """Close a forge session by removing its session and manifest files.

        Deletes:
        - The active session file (active_{hash}.json or active.json)
        - The session-scoped manifest (manifest_{session_id}.json),
          found by reading session_id from the active file
        - Legacy manifest.json if present (backward compat cleanup)

        Args:
            target: If a string, remove the scoped file for that target.
                    If None/omitted, remove legacy active.json.
            wave_id: Bundle D — when scoped, also scopes by wave_id so
                     closing wave K leaves wave L intact.
        """
        if target is not ...:
            fname = _session_filename(target, wave_id)
        else:
            fname = _session_filename(None)  # "active.json"
        active_path = MANIFEST_DIR / fname

        # Read session_id from active file to find scoped manifest
        session_id = None
        if active_path.exists():
            try:
                data = json.loads(active_path.read_text(encoding="utf-8"))
                session_id = data.get("session_id")
            except (json.JSONDecodeError, OSError):
                pass
            active_path.unlink()

        # Delete session-scoped manifest
        if session_id:
            manifest_path = MANIFEST_DIR / f"manifest_{session_id}.json"
            if manifest_path.exists():
                manifest_path.unlink()

        # Clean up legacy manifest.json
        legacy = MANIFEST_DIR / "manifest.json"
        if legacy.exists():
            legacy.unlink()
