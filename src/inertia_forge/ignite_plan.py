"""Agent-backed planning — Vector turns intent into a structured plan.

Dispatches the forge's planning agent (Vector, from the bundled roster) and
parses its markdown into a structured PlanOutput: summary, phases, files to
touch, a complexity estimate, and risks. The dispatch is the only LLM touchpoint
(Vector is read-only); the parsing is deterministic — the agent proposes, the
structure is extracted by rule.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_PLAN_PROMPT = (
    "Analyze the goal below and produce a detailed implementation plan. Format "
    "your response with these exact sections:\n"
    "## Summary\n## Phases (each as '### Phase N: name' with '- ' task bullets)\n"
    "## Files to Modify\n## Complexity (one word: low / medium / high)\n## Risks\n\n"
    "---\n\nGoal:\n"
)


@dataclass
class PlanPhase:
    name: str
    tasks: list[str] = field(default_factory=list)


@dataclass
class PlanOutput:
    summary: str = ""
    phases: list[PlanPhase] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    complexity: str = "medium"
    risks: list[str] = field(default_factory=list)
    raw: str = ""

    def to_dict(self) -> dict:
        return {"summary": self.summary, "complexity": self.complexity,
                "phases": [{"name": p.name, "tasks": p.tasks} for p in self.phases],
                "files": self.files, "risks": self.risks}


def _section(text: str, name: str) -> str:
    m = re.search(rf"##\s*{name}[^\n]*\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _bullets(block: str) -> list[str]:
    return [ln.strip().lstrip("-*").strip() for ln in block.splitlines()
            if ln.strip().startswith(("-", "*")) and ln.strip().lstrip("-*").strip()]


def parse_plan(text: str) -> PlanOutput:
    """Parse a planner agent's markdown into a structured PlanOutput."""
    phases: list[PlanPhase] = []
    block = _section(text, "Phases?")
    for chunk in re.split(r"###\s*Phase\s*\d*:?\s*", block, flags=re.IGNORECASE):
        if not chunk.strip():
            continue
        lines = chunk.strip().splitlines()
        phases.append(PlanPhase(name=lines[0].strip(), tasks=_bullets("\n".join(lines[1:]))))
    cx = re.search(r"\b(low|medium|high)\b", _section(text, "Complexity"), re.IGNORECASE)
    return PlanOutput(
        summary=_section(text, "Summary"), phases=phases,
        files=_bullets(_section(text, "Files[^\\n]*")),
        complexity=cx.group(1).lower() if cx else "medium",
        risks=_bullets(_section(text, "Risks?")), raw=text)


def plan_goal(goal: str, cli: str = "claude", model: str | None = None,
              root: Path | None = None, dispatcher=None) -> PlanOutput | None:
    """Dispatch Vector to plan *goal*; return a structured PlanOutput, or None."""
    prompt = _PLAN_PROMPT + goal
    if dispatcher is not None:
        text = dispatcher(prompt)
    else:
        from inertia_forge.invoker import dispatch
        resp = dispatch("vector", prompt, cli=cli, model=model, working_dir=root or Path("."))
        text = None if resp.is_error else resp.result
    return parse_plan(text) if text is not None else None


def run_plan_cli(argv: list[str]) -> int:
    import argparse
    import json
    from inertia_forge.glyphs import g, seal
    p = argparse.ArgumentParser(prog="inertia-forge ignite plan")
    p.add_argument("goal", nargs="+", help="the goal to plan")
    p.add_argument("--agent", default="claude", help="LLM provider")
    p.add_argument("--model", default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    out = plan_goal(" ".join(args.goal), cli=args.agent, model=args.model)
    if out is None:
        print(f"{seal('error')} planning failed — agent returned an error")
        return 1
    if args.json:
        print(json.dumps(out.to_dict(), indent=2))
        return 0
    print(f"{seal('ok')} plan ({out.complexity} complexity)")
    print(f"  {out.summary}" if out.summary else "  (no summary)")
    for ph in out.phases:
        print(f"\n{g('dot')} {ph.name}")
        for task in ph.tasks:
            print(f"    - {task}")
    if out.risks:
        print("\nrisks: " + "; ".join(out.risks))
    return 0
