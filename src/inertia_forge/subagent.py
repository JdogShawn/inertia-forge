"""Manage Claude Code subagents — `.claude/agents/<name>.md`. Deterministic CRUD.

Scaffolds, lists, shows, validates, and removes subagent definitions (YAML
frontmatter: name/description/tools, then a system-prompt body). No LLM —
pure file management of the agent registry.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

AGENTS = Path(".claude") / "agents"


def _path(name: str) -> Path:
    return AGENTS / f"{name}.md"


def create(name: str, description: str, tools: str, prompt: str) -> Path:
    AGENTS.mkdir(parents=True, exist_ok=True)
    fm = f"---\nname: {name}\ndescription: {description}\n"
    if tools:
        fm += f"tools: {tools}\n"
    body = prompt or f"You are the {name} subagent. Describe your role and method here."
    path = _path(name)
    path.write_text(fm + "---\n\n" + body + "\n", encoding="utf-8")
    return path


def list_agents() -> list[str]:
    return sorted(p.stem for p in AGENTS.glob("*.md")) if AGENTS.exists() else []


def parse(name: str) -> dict | None:
    path = _path(name)
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    d = {"name": name, "description": "", "tools": "", "body": text.strip()}
    if m:
        d["body"] = m.group(2).strip()
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                d[k.strip()] = v.strip()
    return d


def validate_agent(name: str) -> list[str]:
    d = parse(name)
    if d is None:
        return [f"{name}: not found"]
    issues = []
    if not d.get("name"):
        issues.append(f"{name}: missing 'name'")
    if not d.get("description"):
        issues.append(f"{name}: missing 'description'")
    if not d.get("body"):
        issues.append(f"{name}: empty system prompt")
    return issues


def run_subagent(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge subagent")
    sub = p.add_subparsers(dest="sub", required=True)
    sub.add_parser("list")
    c = sub.add_parser("create")
    c.add_argument("name")
    c.add_argument("--description", default="")
    c.add_argument("--tools", default="")
    c.add_argument("--prompt", default="")
    sh = sub.add_parser("show"); sh.add_argument("name")
    rm = sub.add_parser("rm"); rm.add_argument("name")
    va = sub.add_parser("validate"); va.add_argument("name", nargs="?")
    args = p.parse_args(argv)

    if args.sub == "create":
        print(f"created {create(args.name, args.description, args.tools, args.prompt)}")
        return 0
    if args.sub == "show":
        d = parse(args.name)
        if d is None:
            print(f"no such subagent: {args.name}")
            return 1
        print(f"name: {d['name']}\ndescription: {d['description']}\ntools: {d['tools'] or '(all)'}\n")
        print(d["body"])
        return 0
    if args.sub == "rm":
        path = _path(args.name)
        if path.exists():
            path.unlink()
            print(f"removed {args.name}")
            return 0
        print(f"no such subagent: {args.name}")
        return 1
    if args.sub == "validate":
        names = [args.name] if args.name else list_agents()
        issues = [i for n in names for i in validate_agent(n)]
        if issues:
            print("\n".join(f"  - {i}" for i in issues))
            return 1
        print(f"OK: {len(names)} subagent(s) valid")
        return 0
    agents = list_agents()
    print("\n".join(f"  {a}" for a in agents) if agents else "(no subagents)")
    return 0
