"""Structured output envelope — the forge speaks JSON for the agents that drive it.

Every machine-readable response uses one schema, always::

    {"status": "ok" | "error", "data": <payload>, "errors": [<string>, ...]}

so an LLM consuming the forge parses one shape. `inertia-forge json <query>`
emits these; programs import wrap_ok / wrap_error / emit directly.
"""
from __future__ import annotations

import json
from typing import Any


def wrap_ok(data: Any) -> dict:
    """A success envelope carrying *data*."""
    return {"status": "ok", "data": data, "errors": []}


def wrap_error(message: str, data: Any = None) -> dict:
    """An error envelope carrying a message (and optional partial data)."""
    return {"status": "error", "data": data, "errors": [message]}


def emit(envelope: dict) -> int:
    """Print *envelope* as deterministic JSON; return 0 if ok, else 1."""
    print(json.dumps(envelope, indent=2, sort_keys=True, default=str))
    return 0 if envelope.get("status") == "ok" else 1
