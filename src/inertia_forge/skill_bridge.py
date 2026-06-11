"""ForgeSkillBridge — auto-start forge session when a skill is invoked.

Battle Scar #15 fix: the bridge between skill invocation and forge enforcement.
Every skill invocation creates a forge session BEFORE any phase runs.

Usage from SKILL.md:
  Step 0: Run `python -m inertia_forge.skill_bridge start <skill_name> <target>`

Usage programmatically:
  bridge = ForgeSkillBridge("purge", "inertia/doctor/")
  bridge.start_session()
  # ... run phases ...
  bridge.close_session()
"""
from __future__ import annotations

import sys
from pathlib import Path

from inertia_forge import persisted_manifest as pm_mod
from inertia_forge.persisted_manifest import PersistedManifest
from inertia_forge.skill_registry import validate_skill_name


def _print_banner(message: str) -> None:
    """Print a boxed banner. Keeps close_session() compact."""
    bar = "=" * 60
    print(f"\n{bar}\n {message}\n{bar}\n")


def _display_blocking_findings(findings: list[dict]) -> None:
    """Print P0/P1 finding messages (Bypass #19 fix). Helper keeps
    record_phase() under the function-length ceiling."""
    for f in findings:
        sev = f.get("severity")
        if sev in ("P0", "P1"):
            print(f"  [{sev}] {f.get('message', '')}")


class ForgeSkillBridge:
    """Connects skill invocation to forge enforcement."""

    def __init__(self, skill_name: str, target: str,
                 claude_session_id: str = "", wave_id: str = "") -> None:
        self._skill = skill_name.replace("-", "_")
        self._target = target
        self._claude_session_id = claude_session_id
        self._wave_id = wave_id  # Bundle D: scopes the session per-wave
        self._manifest: PersistedManifest | None = None

    def start_session(self) -> dict:
        """Create forge session. Must be called BEFORE any skill phase."""
        # Check if previous session exists for SAME (target, wave_id)
        # — Bundle D scopes by wave so parallel waves don't collide.
        if PersistedManifest.session_exists(
            target=self._target, wave_id=self._wave_id,
        ):
            return {
                "started": False,
                "reason": "Previous session exists. Resume or close it first.",
                "action": "Run: python -m inertia_forge.skill_bridge resume",
            }

        # Validate skill name (Bypass #9 fix)
        if not validate_skill_name(self._skill):
            print(f"WARNING: Skill '{self._skill}' has no YAML definition. "
                  f"Running WITHOUT full enforcement.", file=sys.stderr)

        self._manifest = PersistedManifest(
            self._skill, self._target,
            self._claude_session_id, self._wave_id,
        )
        self._manifest.create_session_file()
        self._manifest.save()
        wave_label = f" Wave: {self._wave_id}" if self._wave_id else ""
        _print_banner(
            f"FORGE SESSION ACTIVE — Skill: {self._skill} "
            f"Target: {self._target}{wave_label}",
        )
        return {
            "started": True, "skill": self._skill,
            "target": self._target, "wave_id": self._wave_id,
        }

    def _load_existing(self) -> PersistedManifest | None:
        """Reconstruct PersistedManifest from on-disk for fresh subprocesses."""
        import json as _json

        from inertia_forge.persisted_manifest import (
            MANIFEST_DIR,
            _session_filename,
        )

        active_path = MANIFEST_DIR / _session_filename(
            self._target, self._wave_id,
        )
        if not active_path.exists():
            return None
        try:
            active_data = _json.loads(active_path.read_text(encoding="utf-8"))
        except (OSError, _json.JSONDecodeError):
            return None
        sid = active_data.get("session_id")
        if not sid:
            return None
        manifest_path = MANIFEST_DIR / f"manifest_{sid}.json"
        if not manifest_path.exists():
            return None
        try:
            manifest_data = _json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, _json.JSONDecodeError):
            return None

        pm = PersistedManifest(self._skill, self._target)
        pm._session_id = sid
        pm._started_at = active_data.get("started_at", pm._started_at)
        phases = manifest_data.get("phases", {})
        if isinstance(phases, dict):
            pm._phases = phases
        return pm

    def record_phase(self, phase_name: str, target_dir: Path | None = None) -> dict:
        """Record phase with mode-dispatched evidence; auto-close on last green gate."""
        if self._manifest is None:
            self._manifest = self._load_existing()
        if self._manifest is None:
            return {"recorded": False, "reason": "No active session. Call start_session() first."}
        from inertia_forge.evidence_collectors import collect
        from inertia_forge.skill_registry import get_evidence_mode

        analysis_dir = target_dir or Path(self._target)
        findings, evidence_hash = collect(
            self._skill, phase_name, self._target,
            analysis_dir, get_evidence_mode(self._skill, phase_name),
        )
        findings = self._unknown_phase_findings(phase_name) + findings

        # Record with computed severity (Battle Scar #14 fix)
        self._manifest.record_phase(phase_name, findings, evidence_hash)

        p0 = sum(1 for f in findings if f["severity"] == "P0")
        p1 = sum(1 for f in findings if f["severity"] == "P1")

        _display_blocking_findings(findings)
        auto_closed = self._maybe_auto_close(p0)

        return {
            "recorded": True, "phase": phase_name,
            "p0": p0, "p1": p1,
            "findings": len(findings),
            "evidence_hash": evidence_hash[:16],
            "blocked": p0 > 0,
            "auto_closed": auto_closed,
        }

    def _unknown_phase_findings(self, phase_name: str) -> list[dict]:
        """F7: synthesize a P0 finding when phase_name isn't a defined step.

        Returns [] if the phase is in the skill's step list (legitimate
        recording) or if the skill itself isn't registered (fail-open).
        """
        try:
            from inertia_forge.skill_registry import get_skill
            skill = get_skill(self._skill)
        except (ValueError, ImportError):
            return []
        if phase_name in skill.steps:
            return []
        return [{
            "severity": "P0",
            "rule": "unknown_phase",
            "file": "<phase_name>",
            "line": 0,
            "message": (
                f"phase '{phase_name}' not in skill '{self._skill}' "
                f"steps: {list(skill.steps)}"
            ),
        }]

    def _maybe_auto_close(self, p0: int) -> bool:
        """Auto-close when THIS session's last blocking gate flips green.

        Bundle D: uses count_gates_for_session(target, wave_id) so a
        wave's auto-close depends only on that wave's gates — parallel
        waves on the same target close independently.

        F5 fix (Donatello Bundle A): symmetric with manual close_session,
        auto-close also refuses while ANY recorded phase carries an empty
        evidence_hash.
        """
        if p0 != 0:
            return False
        if self._check_evidence_hashes():
            return False
        from inertia_forge.completion_lock import count_gates_for_session

        if count_gates_for_session(self._target, self._wave_id) != 0:
            return False
        PersistedManifest.close_session(
            target=self._target, wave_id=self._wave_id,
        )
        self._cleanup_death_note_artifacts()
        self._manifest = None
        return True

    def check_status(self) -> dict:
        """Check current session status."""
        if self._manifest is None:
            return {"active": False}
        consistency = self._manifest.check_consistency()
        return {
            "active": True,
            "zero_debt": self._manifest.is_zero_debt(),
            "consistency_issues": consistency,
        }

    def close_session(self) -> dict:
        """Close the forge session.

        Idempotent: after record_phase auto-closes, returns success.
        Refuses to close if incomplete blocking gates remain or any phase
        is missing its evidence_hash.
        """
        if self._manifest is None:
            if not PersistedManifest.session_exists(
                target=self._target, wave_id=self._wave_id,
            ):
                return {"closed": True, "already_closed": True}
            return {"closed": False, "reason": "No active session"}

        from inertia_forge.completion_lock import count_incomplete_blocking_gates

        remaining = count_incomplete_blocking_gates()
        if remaining > 0:
            _print_banner(f"FORGE SESSION CANNOT CLOSE — {remaining} blocking gate(s) remain.")
            return {
                "closed": False,
                "reason": f"{remaining} blocking gate(s) remain incomplete",
            }

        missing = self._check_evidence_hashes()
        if missing:
            _print_banner(
                f"FORGE SESSION CANNOT CLOSE — {len(missing)} phase(s) missing "
                f"evidence_hash: {', '.join(missing)}",
            )
            return {
                "closed": False,
                "reason": f"{len(missing)} phase(s) missing evidence hash",
            }

        status = self.check_status()
        PersistedManifest.close_session(
            target=self._target, wave_id=self._wave_id,
        )
        self._cleanup_death_note_artifacts()
        _print_banner(f"FORGE SESSION CLOSED — Zero debt: {status.get('zero_debt', False)}")
        for issue in status.get("consistency_issues") or []:
            print(f"  WARNING: {issue}")
        self._manifest = None
        return {"closed": True, **status}


    def _check_evidence_hashes(self) -> list[str]:
        """Return phase names that are missing a non-empty evidence_hash."""
        if self._manifest is None:
            return []
        missing: list[str] = []
        for name, data in self._manifest._phases.items():
            if not data.get("evidence_hash"):
                missing.append(name)
        return missing

    @staticmethod
    def _cleanup_death_note_artifacts() -> None:
        """Delegate to skill_bridge_cli.cleanup_death_note_artifacts."""
        from inertia_forge.skill_bridge_cli import cleanup_death_note_artifacts
        cleanup_death_note_artifacts()


# ── Checkpoint Helper ──────────────────────────────────────────


def _run_checkpoint() -> int:
    """Save manifest to checkpoint file. Silent on stdout."""
    import json
    import shutil

    manifest_dir = pm_mod.MANIFEST_DIR
    checkpoint_path = manifest_dir / "manifest_checkpoint.json"

    # No active session => exit silently (check any scoped or legacy file)
    if not PersistedManifest.session_exists():
        return 0

    # Find a manifest to checkpoint: prefer session-scoped, fall back to legacy
    source_path = None
    if manifest_dir.exists():
        for active_file in sorted(manifest_dir.glob("active*.json")):
            try:
                data = json.loads(active_file.read_text(encoding="utf-8"))
                sid = data.get("session_id")
                if sid:
                    candidate = manifest_dir / f"manifest_{sid}.json"
                    if candidate.exists():
                        source_path = candidate
                        break
            except (json.JSONDecodeError, OSError):
                continue

    # Fall back to legacy manifest.json
    if source_path is None:
        legacy = pm_mod.MANIFEST_PATH
        if legacy.exists():
            source_path = legacy

    if source_path is None:
        return 0

    shutil.copy2(str(source_path), str(checkpoint_path))
    print("Forge checkpoint saved.", file=sys.stderr)
    return 0


# ── CLI Entry Point ────────────────────────────────────────────


def _build_parser():
    """Construct the skill_bridge CLI argument parser."""
    import argparse

    parser = argparse.ArgumentParser(prog="skill_bridge")
    sub = parser.add_subparsers(dest="command")

    start_p = sub.add_parser("start", help="Start forge session")
    start_p.add_argument("skill", help="Skill name (e.g., purge)")
    start_p.add_argument("target", help="Target directory")
    start_p.add_argument(
        "--wave", default="",
        help="Bundle D: wave_id namespace for parallel waves on same target",
    )

    rec_p = sub.add_parser(
        "record-phase",
        help="Record a phase (quality-checked, auto-closes on final pass)",
    )
    rec_p.add_argument("phase", help="Phase name from the skill's step list")
    rec_p.add_argument("target", help="Target directory")
    rec_p.add_argument(
        "--wave", default="",
        help="Bundle D: wave_id namespace; must match the wave used at start",
    )

    sub.add_parser("status", help="Check session status")
    sub.add_parser("close", help="Close session")
    sub.add_parser("checkpoint", help="Save manifest checkpoint")
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI: python -m inertia_forge.skill_bridge <subcommand> ..."""
    from inertia_forge import skill_bridge_cli as _cli

    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "start":
        bridge = ForgeSkillBridge(args.skill, args.target, wave_id=args.wave)
        result = bridge.start_session()
        return 0 if result.get("started") else 1
    elif args.command == "record-phase":
        return _cli.run_record_phase(args.phase, args.target, args.wave)
    elif args.command == "status":
        return _cli.run_status()
    elif args.command == "close":
        return _cli.run_close()
    elif args.command == "checkpoint":
        return _run_checkpoint()

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
