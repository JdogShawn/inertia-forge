"""Native session continuity — `.forge/state.json`.

A tiny "what was just done / what's next" ledger so multi-session work picks up
cleanly — INERTIA's native continuity ledger, dependency-free.

Shape::

    {"last": "...", "next": "...",
     "history": [{"done": "...", "next": "..."}]}   # newest last
"""
from __future__ import annotations

import json
from pathlib import Path

STATE_FILE = Path(".forge") / "state.json"
_HISTORY_MAX = 100


def load() -> dict:
    if not STATE_FILE.exists():
        return {"last": "", "next": "", "history": []}
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"last": "", "next": "", "history": []}
    data.setdefault("last", "")
    data.setdefault("next", "")
    data.setdefault("history", [])
    return data


def save(data: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def set_progress(done: str = "", next_: str = "") -> dict:
    """Record what was just done and/or what's next. Appends to history
    (bounded) and updates the current last/next pointers."""
    data = load()
    if done:
        data["last"] = done
    if next_:
        data["next"] = next_
    if done or next_:
        data["history"].append({"done": done, "next": next_})
        data["history"] = data["history"][-_HISTORY_MAX:]
    save(data)
    return data
