#!/usr/bin/env bash
# Capture a Claude Code permission-denied event into the forge audit trail
# (signal only — no retry). Wire it to your editor's permission-denied hook if
# supported; it is installed but not auto-wired. View with `inertia-forge log`.
command -v python3 >/dev/null 2>&1 && PY=python3 || PY=python
exec "$PY" -m inertia_forge.hookutil permission-denied
