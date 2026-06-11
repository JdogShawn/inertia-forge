"""Claude Code hook helpers — stdin JSON in, hook behavior out.

The packaged .sh hooks are thin wrappers around these subcommands so all logic
lives in tested Python (no jq dependency):

  status     UserPromptSubmit  — inject the active session banner (owner-scoped)
  autostart  UserPromptSubmit  — start a session when the prompt is /<skill>
  gate       PreToolUse(Bash)  — block forge escape commands (exit 2)
  stopguard  Stop              — block stop while blocking gates remain (exit 2)

Target directory for auto-started sessions: $INERTIA_FORGE_TARGET (default ".").
All subcommands fail OPEN (never crash Claude): unexpected errors exit 0.
"""
from __future__ import annotations

import json
import os
import re
import sys


def _stdin() -> dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, OSError):
        return {}


def _target() -> str:
    return os.environ.get("INERTIA_FORGE_TARGET", ".")


def _owner(data: dict) -> str:
    # Claude Code provides the session id on hook stdin.
    return data.get("session_id") or ""


def cmd_status(data: dict) -> int:
    from inertia_forge.completion_lock import get_forge_status
    status = get_forge_status(_owner(data))
    if status:
        print(f"FORGE SESSION ACTIVE — {status}.")
        print("The only way out is to record each blocking gate's phase:")
        print("  inertia-forge record-phase <PHASE> <TARGET>")
    return 0


_SLASH = re.compile(r"^\s*/([A-Za-z][A-Za-z0-9_-]+)")


def cmd_autostart(data: dict) -> int:
    prompt = data.get("prompt") or ""
    m = _SLASH.match(prompt)
    if not m:
        return 0
    from inertia_forge.persisted_manifest import PersistedManifest
    from inertia_forge.skill_bridge import ForgeSkillBridge
    from inertia_forge.skill_registry import validate_skill_name
    skill = m.group(1)
    if not validate_skill_name(skill):
        return 0
    target, owner = _target(), _owner(data)
    if PersistedManifest.session_exists(target=target, claude_session_id=owner):
        return 0
    ForgeSkillBridge(skill, target, claude_session_id=owner).start_session()
    return 0


# Commands that would let a session escape its gates — blocked at the gate.
# Covers both the module form (`... skill_bridge close`) and the console-script
# form (`inertia-forge close`), plus any direct write against the session dir.
_BLOCKED = (
    r"(skill_bridge|inertia-forge)\b.*\b(close|abandon)\b",
    r"close_session",
    r"\.forge/",  # direct writes/deletes against the session dir
)
# The ONE sanctioned forge command (and the hook helper itself).
_ALLOWED = re.compile(r"record-phase|hookutil")


def cmd_gate(data: dict) -> int:
    command = (data.get("tool_input") or {}).get("command", "")
    # Evaluate each shell segment independently (no `&& pytest` smuggling).
    for seg in re.split(r"&&|\|\||;|\|", command):
        if _ALLOWED.search(seg):
            continue
        for pat in _BLOCKED:
            if re.search(pat, seg):
                try:
                    from inertia_forge.bypass_prevention import log_behavioral_event
                    log_behavioral_event("gate_blocked", f"blocked segment: {seg.strip()[:120]}")
                except Exception:
                    pass
                print(
                    "BLOCKED BY FORGE GATE: forge sessions close only by "
                    "recording all blocking gates — there is no manual "
                    f"close/abandon and no direct .forge write. (segment: {seg.strip()})",
                    file=sys.stderr,
                )
                return 2
    return 0


def cmd_stopguard(data: dict) -> int:
    from inertia_forge.completion_lock import count_incomplete_blocking_gates
    remaining = count_incomplete_blocking_gates(_owner(data))
    if remaining > 0:
        print(
            f"FORGE SESSION ACTIVE — {remaining} blocking gate(s) remaining. "
            "Record every gate's phase before stopping.",
            file=sys.stderr,
        )
        return 2
    return 0


def cmd_contain(data: dict) -> int:
    """PreToolUse(Edit|Write): block writes to blocked/readonly paths when a
    contained session is active. Exit 2 blocks the write."""
    fp = (data.get("tool_input") or {}).get("file_path", "")
    if not fp:
        return 0
    from inertia_forge.containment import classify, is_write_allowed
    if not is_write_allowed(fp):
        try:
            from inertia_forge.bypass_prevention import log_behavioral_event
            log_behavioral_event("containment_blocked", f"write blocked: {fp}")
        except Exception:
            pass
        print(
            f"BLOCKED BY CONTAINMENT: '{fp}' is {classify(fp)} — not writable "
            "in this contained session.",
            file=sys.stderr,
        )
        return 2
    return 0


_COMMANDS = {
    "status": cmd_status,
    "autostart": cmd_autostart,
    "gate": cmd_gate,
    "stopguard": cmd_stopguard,
    "contain": cmd_contain,
}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in _COMMANDS:
        print(f"usage: hookutil {{{'|'.join(_COMMANDS)}}}", file=sys.stderr)
        return 0
    try:
        return _COMMANDS[argv[0]](_stdin())
    except Exception:  # fail-open: never crash Claude on a hook error
        return 0


if __name__ == "__main__":
    sys.exit(main())
