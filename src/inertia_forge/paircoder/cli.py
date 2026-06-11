"""Sanctioned-CLI drift detection.

bpsai-pair is the sanctioned interface for creating/managing tasks. When a
task file's status is changed outside the CLI, `bpsai-pair task list` emits a
"changed outside CLI" warning. The forge consumes that signal to enforce that
task management goes through the CLI, not hand-edited files.

Fail-open: if the CLI can't be run, return no drift (don't block on infra).
"""
from __future__ import annotations

import re
import subprocess
import sys

_TID = re.compile(r"\bT\d+\.\d+\b")


def _parse_drift(text: str) -> list[str]:
    """Extract task IDs flagged as 'changed outside CLI' from CLI output."""
    drifted: list[str] = []
    for line in text.splitlines():
        if "changed outside CLI" in line:
            m = _TID.search(line)
            if m:
                drifted.append(m.group(0))
    return drifted


def drifted_tasks() -> list[str]:
    """Task IDs whose file status diverged from the sanctioned CLI registry."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bpsai_pair", "task", "list"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    return _parse_drift((result.stdout or "") + (result.stderr or ""))
