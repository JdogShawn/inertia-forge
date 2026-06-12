"""Git commit after a successful ignite task.

If the agent already committed its own work since the task started, we only
sweep up any remainder; otherwise we stage everything and make one
``task(ignite): <id> — <title>`` commit. Forge runtime state (the task store,
telemetry db, context pack, run state) is unstaged before committing so it never
lands in a feature commit or causes merge churn.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

# Forge bookkeeping that must never be committed as task output.
_UNSTAGE = [
    ".forge/forge_tasks.json",
    ".forge/telemetry.db",
    ".forge/context_pack.md",
    ".forge/ignite",
    ".forge/session.json",
]
_GIT_TIMEOUT = 15


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True,
        text=True, encoding="utf-8", errors="replace",
        check=False, timeout=_GIT_TIMEOUT,
    )


def _agent_self_committed(root: Path, start_time: str) -> bool:
    """Did the agent make its own commits since the task started?"""
    if not start_time:
        return False
    try:
        r = _git(root, "log", f"--since={start_time}", "--oneline")
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0 and bool(r.stdout.strip())


def _stage_and_commit(root: Path, message: str) -> int:
    """git add -A, unstage forge state, commit. Returns git's return code."""
    add = _git(root, "add", "-A")
    if add.returncode != 0:
        return add.returncode
    _git(root, "reset", "HEAD", "--", *_UNSTAGE)
    commit = _git(root, "commit", "-m", message)
    return commit.returncode


def commit_task(
    root: Path, task_id: str, title: str = "", start_time: str = "",
) -> bool:
    """Commit task output. Returns True if a commit was made (or already present).

    Never raises — git failures are reported via the return value so the ignite
    loop keeps going (a failed commit does not fail the task itself).
    """
    try:
        if _agent_self_committed(root, start_time):
            self_remainder = _stage_and_commit(
                root, f"task(ignite): {task_id} — remaining changes")
            return self_remainder in (0, 1)  # 1 == nothing-to-commit (already done)
        suffix = f" — {title}" if title else ""
        rc = _stage_and_commit(root, f"task(ignite): {task_id}{suffix}")
        return rc == 0
    except (OSError, subprocess.SubprocessError):
        return False
