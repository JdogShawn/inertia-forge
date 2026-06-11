#!/usr/bin/env bash
# PreToolUse(Bash): block forge-escape commands (manual close/abandon, direct
# .forge writes). Exit 2 blocks the tool call. The only sanctioned forge
# command is `record-phase`.
command -v python3 >/dev/null 2>&1 && PY=python3 || PY=python
exec "$PY" -m inertia_forge.hookutil gate
