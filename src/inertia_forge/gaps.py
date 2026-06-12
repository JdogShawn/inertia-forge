"""Deterministic gap detection — what's missing, found by inspection (no LLM).

Surfaces concrete, checkable gaps:
  - skills with blocking gates but no methodology `doc:`
  - skills whose declared `doc:` file doesn't exist
  - tasks with no acceptance criteria or no verification command
  - source modules (.py) with no discoverable test file

Unlike a vague "gap detector", every gap here is a fact you can act on.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def _skill_gaps() -> list[str]:
    from inertia_forge.skill_registry import get_all_skills, get_required_steps
    out = []
    for name, skill in sorted(get_all_skills().items()):
        if get_required_steps(name) and not skill.doc:
            out.append(f"skill {name}: has blocking gates but no methodology doc")
        if skill.doc and not Path(skill.doc).is_file():
            out.append(f"skill {name}: declared doc {skill.doc!r} not found")
    return out


def _task_gaps() -> list[str]:
    from inertia_forge import tasks as t
    out = []
    for task in t.list_tasks():
        if not task.get("acceptance_criteria"):
            out.append(f"task {task['id']}: no acceptance criteria")
        if not task.get("verification"):
            out.append(f"task {task['id']}: no verification command (not TDD-ready)")
    return out


def _test_gaps(src: Path) -> list[str]:
    if not src.is_dir():
        return []
    tested = {p.stem[len("test_"):] for p in src.rglob("test_*.py")}
    out = []
    for py in sorted(src.rglob("*.py")):
        # Match on the FILENAME and path PARTS, never a substring of the full
        # path (a temp dir like 'test_xyz0' would falsely match a substring).
        if py.name.startswith("test_") or py.name.endswith("_test.py") or py.name == "__init__.py":
            continue
        if any(part in ("tests", "__pycache__") for part in py.parts):
            continue
        if py.stem not in tested:
            out.append(f"module {py.name}: no test_{py.stem}.py found")
    return out


def detect(src: str = "src") -> list[str]:
    return _skill_gaps() + _task_gaps() + _test_gaps(Path(src))


def run_gaps(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge gaps")
    p.add_argument("src", nargs="?", default="src", help="source dir for test-coverage gaps")
    args = p.parse_args(argv)
    found = detect(args.src)
    if not found:
        print("OK: no gaps detected")
        return 0
    for g in found:
        print(f"  - {g}")
    print(f"\n{len(found)} gap(s)")
    return 1
