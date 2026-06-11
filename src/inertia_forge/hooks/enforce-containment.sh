#!/usr/bin/env bash
# PreToolUse(Edit|Write): block writes to blocked/readonly paths when a
# contained INERTIA session is active. Silent when containment is off.
command -v python3 >/dev/null 2>&1 && PY=python3 || PY=python
exec "$PY" -m inertia_forge.hookutil contain
