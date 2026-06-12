"""Store integrity — validate the forge's own JSON stores are well-formed.

Deterministic schema checks on ``.forge/forge_tasks.json`` and
``.forge/config.json``: parseable JSON, the expected top-level shape, and task
records carrying the required fields with valid ids and statuses.
`validate-store` reports problems and exits 1 — it catches a hand-edit or a
partial write before a corrupt store can mislead a gate.
"""
from __future__ import annotations

import json
from pathlib import Path

from inertia_forge import tasks as t

_REQUIRED_FIELDS = ("title", "status", "acceptance_criteria", "verification")


def _load(name: str) -> tuple[object, str | None]:
    path = Path(".forge") / name
    if not path.exists():
        return None, None
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, json.JSONDecodeError) as e:
        return None, f"{name}: invalid JSON ({e})"


def check_tasks() -> list[str]:
    data, err = _load("forge_tasks.json")
    if err:
        return [err]
    if data is None:
        return []
    if not isinstance(data, dict):
        return ["forge_tasks.json: top level must be an object"]
    tasks = data.get("tasks", {})
    if not isinstance(tasks, dict):
        return ["forge_tasks.json: 'tasks' must be an object"]
    out: list[str] = []
    for tid, task in tasks.items():
        if not t.TASK_ID_RE.match(tid):
            out.append(f"{tid}: id key is not T<sprint>.<seq>")
        if not isinstance(task, dict):
            out.append(f"{tid}: record must be an object")
            continue
        out += [f"{tid}: missing field '{f}'" for f in _REQUIRED_FIELDS if f not in task]
        if task.get("status") not in t.VALID_STATUSES:
            out.append(f"{tid}: invalid status {task.get('status')!r}")
    return out


def check_config() -> list[str]:
    data, err = _load("config.json")
    if err:
        return [err]
    if data is not None and not isinstance(data, dict):
        return ["config.json: must be an object"]
    return []


def run_validate_store(_argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    issues = check_tasks() + check_config()
    if not issues:
        print(f"{seal('ok')} stores valid")
        return 0
    for msg in issues:
        print(f"{seal('error')} {msg}")
    return 1
