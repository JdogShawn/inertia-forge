"""Bundled INERTIA assets — the agent roster + skill methodology docs.

The forge is *for LLMs to use*: agents are the roles an LLM adopts, skills are
the methodology it follows, and the forge gates the result. These ship with the
package and install into a project's `.claude/` via `inertia-forge init`.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"
AGENTS = ASSETS / "agents"
SKILLS = ASSETS / "skills"
COMMANDS = ASSETS / "commands"
RULES = ASSETS / "rules"
SCAFFOLD = ASSETS / "scaffold"


def _install_flat(src_dir: Path, dst_dir: Path) -> list[str]:
    dst_dir.mkdir(parents=True, exist_ok=True)
    out = []
    for src in src_dir.glob("*.md"):
        shutil.copy2(src, dst_dir / src.name)
        out.append(src.stem)
    return sorted(out)


def agent_names() -> list[str]:
    return sorted(p.stem for p in AGENTS.glob("*.md")) if AGENTS.exists() else []


def skill_names() -> list[str]:
    return sorted(p.name for p in SKILLS.iterdir() if (p / "SKILL.md").exists()) if SKILLS.exists() else []


def install_agents(target: Path) -> list[str]:
    """Copy the agent roster into <target>/.claude/agents/. Returns names installed."""
    dst = target / ".claude" / "agents"
    dst.mkdir(parents=True, exist_ok=True)
    out = []
    for src in AGENTS.glob("*.md"):
        shutil.copy2(src, dst / src.name)
        out.append(src.stem)
    return sorted(out)


def install_skills(target: Path) -> list[str]:
    """Copy skill methodology docs into <target>/.claude/skills/<name>/SKILL.md."""
    out = []
    for name in skill_names():
        dst = target / ".claude" / "skills" / name
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SKILLS / name / "SKILL.md", dst / "SKILL.md")
        out.append(name)
    return out


def install_commands(target: Path) -> list[str]:
    """Copy INERTIA slash commands into <target>/.claude/commands/."""
    return _install_flat(COMMANDS, target / ".claude" / "commands")


def install_rules(target: Path) -> list[str]:
    """Copy the architecture rules into <target>/.claude/rules/."""
    return _install_flat(RULES, target / ".claude" / "rules")


def install_scaffold(target: Path) -> list[str]:
    """Write CLAUDE.md (root) + .forge/context/ docs. Never overwrites existing."""
    written = []
    claude = target / "CLAUDE.md"
    if not claude.exists():
        shutil.copy2(SCAFFOLD / "CLAUDE.md", claude)
        written.append("CLAUDE.md")
    ctx_dst = target / ".forge" / "context"
    ctx_dst.mkdir(parents=True, exist_ok=True)
    for src in (SCAFFOLD / "context").glob("*.md"):
        dst = ctx_dst / src.name
        if not dst.exists():
            shutil.copy2(src, dst)
            written.append(f"context/{src.name}")
    return written


def install_agent_memory(target: Path) -> list[str]:
    """Seed a starter MEMORY.md for each bundled agent under .claude/agent-memory/."""
    out = []
    for name in agent_names():
        path = target / ".claude" / "agent-memory" / name / "MEMORY.md"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                f"# {name} — memory\n\nDurable lessons this agent has learned "
                "about this project.\n\n", encoding="utf-8")
        out.append(name)
    return out


def run_agents(argv: list[str]) -> int:
    """inertia-forge agents [show <name>] — the bundled INERTIA agent roster."""
    import argparse
    p = argparse.ArgumentParser(prog="inertia-forge agents")
    sub = p.add_subparsers(dest="sub")
    sh = sub.add_parser("show")
    sh.add_argument("name")
    sub.add_parser("install").add_argument("dir", nargs="?", default=".")
    args, _ = p.parse_known_args(argv)
    if args.sub == "show":
        path = AGENTS / f"{args.name}.md"
        if not path.exists():
            print(f"no such agent: {args.name}")
            return 1
        print(path.read_text(encoding="utf-8"))
        return 0
    if args.sub == "install":
        target = Path(argv[1]) if len(argv) > 1 else Path(".")
        names = install_agents(target) + install_skills(target)
        print(f"installed: {', '.join(names)}")
        return 0
    for name in agent_names():
        first = (AGENTS / f"{name}.md").read_text(encoding="utf-8")
        desc = ""
        for line in first.splitlines():
            if line.startswith("description:"):
                desc = line.split(":", 1)[1].strip()
                break
        print(f"  {name:10} {desc[:80]}")
    return 0
