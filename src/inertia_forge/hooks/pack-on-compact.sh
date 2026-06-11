#!/usr/bin/env bash
# PreCompact: snapshot forge context (state + plan + tasks + audit) to
# .forge/context_pack.md so it survives a Claude Code compaction event.
command -v python3 >/dev/null 2>&1 && PY=python3 || PY=python
exec "$PY" -m inertia_forge.cli pack
