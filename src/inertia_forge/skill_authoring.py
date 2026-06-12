"""Skill authoring — scaffold a new skill, and score a registered one. Zero LLM."""
from __future__ import annotations

import argparse
from pathlib import Path

_SKILL_TEMPLATE = """# {title}

> One-line purpose. Evidence mode: stamped. Agent: <agent>.

## When to use
Describe the trigger that should invoke this skill.

## The phases
### 1. first_step  (blocking)
What the agent does, and what evidence proves it.

### 2. second_step
...

## Done
The exit criteria — what makes every gate green.
"""

_REGISTRY_SNIPPET = """# add to your skills YAML:
{name}:
  loop_max: 0
  evidence_mode: stamped
  doc: .claude/skills/{slug}/SKILL.md
  steps:
    - first_step
    - second_step
  gates:
    first_step: blocking
"""


def new(name: str) -> Path:
    slug = name.replace("_", "-")
    dst = Path(".claude") / "skills" / slug
    dst.mkdir(parents=True, exist_ok=True)
    path = dst / "SKILL.md"
    if not path.exists():
        path.write_text(_SKILL_TEMPLATE.format(title=name.replace("_", " ").title()),
                        encoding="utf-8")
    return path


def score(name: str) -> tuple[int, int, list[str]]:
    """Score a registered skill 0..5 with notes on what's missing."""
    from inertia_forge.skill_registry import get_required_steps, get_skill
    try:
        sk = get_skill(name)
    except ValueError:
        return 0, 5, [f"{name}: not registered"]
    pts, notes = 0, []
    if sk.steps:
        pts += 1
    else:
        notes.append("no steps defined")
    if get_required_steps(name):
        pts += 1
    else:
        notes.append("no blocking gates")
    if sk.evidence_mode:
        pts += 1
    if sk.doc:
        pts += 1
        if Path(sk.doc).is_file():
            pts += 1
        else:
            notes.append("doc declared but file missing")
    else:
        notes.append("no methodology doc (doc:)")
    return pts, 5, notes


def run_skill_new(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge skills new")
    p.add_argument("name")
    args = p.parse_args(argv)
    path = new(args.name)
    print(f"scaffolded {path}\n")
    print(_REGISTRY_SNIPPET.format(name=args.name, slug=args.name.replace("_", "-")))
    return 0


def run_skill_score(argv: list[str]) -> int:
    from inertia_forge.skill_registry import get_all_skills
    p = argparse.ArgumentParser(prog="inertia-forge skills score")
    p.add_argument("name", nargs="?")
    args = p.parse_args(argv)
    names = [args.name] if args.name else sorted(get_all_skills())
    worst = 0
    for name in names:
        pts, total, notes = score(name)
        flag = "" if pts == total else "  <- " + "; ".join(notes)
        print(f"  {name:28} {pts}/{total}{flag}")
        worst = max(worst, total - pts)
    return 1 if worst else 0
