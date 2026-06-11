#!/usr/bin/env bash
# UserPromptSubmit: start a forge session when the prompt is /<skill>.
# Silent unless the leading token is a registered skill with no active session.
command -v python3 >/dev/null 2>&1 && PY=python3 || PY=python
exec "$PY" -m inertia_forge.hookutil autostart
