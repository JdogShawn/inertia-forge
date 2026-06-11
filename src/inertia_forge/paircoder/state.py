"""Deterministic readers for bpsai-pair (PairCoder) on-disk state.

Pure file/JSON reads under .paircoder (relative to cwd — the forge runs from
the project root). Split out of paircoder_evidence so each module stays under
the architecture function-count limit. No bpsai-pair import; the .task.md /
.plan.yaml / active_task.json shapes are the stable contract.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

PAIRCODER = Path(".paircoder")
PLANS_DIR = PAIRCODER / "plans"
TASKS_DIR = PAIRCODER / "tasks"
ACTIVE_TASK = PAIRCODER / "enforcement" / "active_task.json"

VALID_PLAN_TYPES = ("feature", "bugfix", "refactor", "chore")
_TASK_ID_RE = re.compile(r"^T\d+\.\d+$")


def read(path: Path) -> str | None:
    """Read a file's text, or None on error."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _frontmatter(text: str, key: str) -> str | None:
    m = re.search(rf"^{key}:\s*(\S+)", text, re.MULTILINE)
    return m.group(1).strip().strip("'\"") if m else None


def plan_files() -> list[Path]:
    return sorted(PLANS_DIR.glob("*.plan.yaml")) if PLANS_DIR.exists() else []


def plan_type(plan_path: Path) -> str | None:
    text = read(plan_path)
    return _frontmatter(text, "type") if text else None


def task_files() -> list[Path]:
    return sorted(TASKS_DIR.glob("*.task.md")) if TASKS_DIR.exists() else []


def task_id(task_path: Path) -> str | None:
    text = read(task_path)
    fm = _frontmatter(text, "id") if text else None
    # Fall back to the filename stem (strip the .task suffix).
    return fm or task_path.name.replace(".task.md", "") or None


def task_id_valid(tid: str) -> bool:
    return bool(_TASK_ID_RE.match(tid))


def complexity_value(task_path: Path) -> float | None:
    """Parsed complexity estimate, or None if absent/non-numeric."""
    text = read(task_path)
    if not text:
        return None
    raw = _frontmatter(text, "complexity")
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def ac_total(text: str) -> int:
    """Total acceptance-criteria checkboxes (checked + unchecked)."""
    return len(re.findall(r"^\s*-\s*\[[ xX]\]", text, re.MULTILINE))


def active_task_id() -> str | None:
    if not ACTIVE_TASK.exists():
        return None
    try:
        data = json.loads(ACTIVE_TASK.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return (data.get("task_id") or "").strip() or None


def read_active_task() -> str | None:
    """Full text of the active task's .task.md, or None if absent."""
    tid = active_task_id()
    if tid is None:
        return None
    return read(TASKS_DIR / f"{tid}.task.md")


def status_of(text: str) -> str | None:
    return _frontmatter(text, "status")


def unchecked_ac(text: str) -> int:
    return len(re.findall(r"^\s*-\s*\[ \]", text, re.MULTILINE))


def has_verification(text: str) -> bool:
    """True if the task carries a Verification section (TDD-ready)."""
    return bool(re.search(r"^#+\s*Verification\b", text, re.MULTILINE | re.IGNORECASE))
