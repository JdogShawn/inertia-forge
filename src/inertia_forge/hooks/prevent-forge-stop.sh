#!/usr/bin/env bash
# Stop: refuse to stop while the owning session has blocking gates remaining.
# Exit 2 blocks the stop. The session auto-closes when the last gate is green.
command -v python3 >/dev/null 2>&1 && PY=python3 || PY=python
exec "$PY" -m inertia_forge.hookutil stopguard
