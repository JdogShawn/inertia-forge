"""`inertia-forge statusline` — a Claude Code status segment.

Renders the INERTIA atom + forge state for the footer line under the prompt,
so the forge is *visibly* installed and active alongside the model, branch, and
folder. Reads Claude Code's status JSON from stdin (session_id, model,
workspace); it never raises and always prints exactly one line.

Claude Code captures stdout (not a TTY) but renders ANSI, so this forces colour
on — except NO_COLOR, which still wins. Kept dependency-light: the statusline
re-runs on every render (~300ms throttle), so it touches only stdlib + the
forge's own light modules.

Install: `inertia-forge init` wires it into .claude/settings.json, or add

    "statusLine": { "type": "command",
                    "command": "inertia-forge statusline", "padding": 0 }
"""
from __future__ import annotations

import json
import os
import sys


def _read_payload() -> dict:
    """Parse Claude Code's status JSON from stdin; {} if absent/garbage."""
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def _state_segment(session_id: str) -> str:
    """The forge's current state: sealed gates > active task > ready."""
    from inertia_forge.glyphs import g
    from inertia_forge.palette import paint
    try:
        from inertia_forge.completion_lock import count_incomplete_blocking_gates
        gates = count_incomplete_blocking_gates(claude_session_id=session_id)
    except Exception:
        gates = 0
    if gates > 0:
        word = "gate" if gates == 1 else "gates"
        return f"{paint(g('gate_locked'), 'warn')} {paint(f'{gates} {word} sealed', 'warn', bold=True)}"
    try:
        from inertia_forge import tasks as tk
        nxt, tasks = tk.next_task(), tk.list_tasks()
    except Exception:
        nxt, tasks = None, []
    if nxt and tasks:
        done = sum(1 for x in tasks if x["status"] == "done")
        return (f"{paint(g('orbit'), 'go', bold=True)} {paint(nxt['id'], 'text')} "
                f"{paint(g('dot'), 'muted')} {paint(f'{done}/{len(tasks)}', 'muted')}")
    return f"{paint(g('gate_open'), 'success')} {paint('ready', 'success')}"


def render(payload: dict) -> str:
    """Compose the one-line segment: ⚛ INERTIA forge · <state>."""
    from inertia_forge.glyphs import g
    from inertia_forge.palette import paint
    atom = paint(g("atom"), "cyan", bold=True)
    name = f"{paint('INERTIA', 'cyan', bold=True)} {paint('forge', 'violet', bold=True)}"
    seg = _state_segment(str(payload.get("session_id") or ""))
    return f"{atom} {name} {paint(g('dot'), 'muted')} {seg}"


def run_statusline(argv: list[str]) -> int:
    os.environ.setdefault("FORCE_COLOR", "3")  # NO_COLOR still overrides
    from inertia_forge import palette
    palette._TRUECOLOR = None
    palette._LIGHT = None
    try:
        print(render(_read_payload()))
    except Exception:
        print("INERTIA forge")
    return 0
