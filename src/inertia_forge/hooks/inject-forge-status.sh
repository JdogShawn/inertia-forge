#!/usr/bin/env bash
# UserPromptSubmit: inject the active forge session banner (owner-scoped).
# Thin wrapper — all logic lives in inertia_forge.hookutil (tested Python).
command -v python3 >/dev/null 2>&1 && PY=python3 || PY=python
exec "$PY" -m inertia_forge.hookutil status
