"""`inertia-forge init` — install the Claude Code enforcement hooks into a project.

Copies the packaged hook scripts into ``<target>/.claude/hooks/`` and wires
them into ``<target>/.claude/settings.json`` (idempotently):

  UserPromptSubmit -> inject-forge-status.sh, auto-forge-on-slash-command.sh
  PreToolUse(Bash) -> enforce-forge-gate.sh
  Stop             -> prevent-forge-stop.sh
  statusLine       -> inertia-forge statusline  (⚛ INERTIA forge footer segment)

After this, invoking a registered skill in Claude Code opens a forge session
whose blocking gates cannot be skipped — the Stop hook holds the session until
every gate is green.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

_HOOKS_DIR = Path(__file__).parent / "hooks"

# (event, matcher, script) — matcher None means "all tools".
_WIRING = [
    ("UserPromptSubmit", None, "inject-forge-status.sh"),
    ("UserPromptSubmit", None, "auto-forge-on-slash-command.sh"),
    ("PreToolUse", "Bash", "enforce-forge-gate.sh"),
    ("Stop", None, "prevent-forge-stop.sh"),
    ("PreCompact", None, "pack-on-compact.sh"),
    ("PreToolUse", "Edit|Write", "enforce-containment.sh"),
]


def _cmd(script: str) -> str:
    return f'bash "$CLAUDE_PROJECT_DIR/.claude/hooks/{script}"'


def _ensure_hook(settings: dict, event: str, matcher: str | None, script: str) -> bool:
    """Add a hook entry idempotently. Returns True if it was newly added."""
    entries = settings.setdefault("hooks", {}).setdefault(event, [])
    cmd = _cmd(script)
    for entry in entries:
        if matcher is not None and entry.get("matcher") != matcher:
            continue
        if matcher is None and "matcher" in entry:
            continue
        for h in entry.get("hooks", []):
            if h.get("command") == cmd:
                return False  # already wired
        entry.setdefault("hooks", []).append({"type": "command", "command": cmd})
        return True
    new_entry: dict = {"hooks": [{"type": "command", "command": cmd}]}
    if matcher is not None:
        new_entry["matcher"] = matcher
    entries.append(new_entry)
    return True


def _ensure_statusline(settings: dict) -> bool:
    """Install the forge statusLine segment, idempotently. Returns True if newly
    added. Respects a pre-existing custom statusLine (never clobbers the user's)."""
    existing = settings.get("statusLine")
    if isinstance(existing, dict) and existing.get("command"):
        c = existing["command"].lower()
        return False  # ours already, or the user's own — leave it be
    settings["statusLine"] = {
        "type": "command", "command": "inertia-forge statusline", "padding": 0,
    }
    return True


def run_init(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="inertia-forge init")
    parser.add_argument(
        "--target", default=".", help="Project root to install into (default: cwd)",
    )
    args = parser.parse_args(argv)
    root = Path(args.target).resolve()

    hooks_dst = root / ".claude" / "hooks"
    hooks_dst.mkdir(parents=True, exist_ok=True)
    copied = []
    for script in _HOOKS_DIR.glob("*.sh"):
        shutil.copy2(script, hooks_dst / script.name)
        copied.append(script.name)

    settings_path = root / ".claude" / "settings.json"
    settings: dict = {}
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"WARNING: {settings_path} is not valid JSON; not modifying it.")
            settings = None  # type: ignore[assignment]

    added = 0
    statusline = False
    if settings is not None:
        for event, matcher, script in _WIRING:
            if _ensure_hook(settings, event, matcher, script):
                added += 1
        statusline = _ensure_statusline(settings)
        settings_path.write_text(
            json.dumps(settings, indent=2) + "\n", encoding="utf-8",
        )

    from inertia_forge import assets
    counts = {
        "agents": len(assets.install_agents(root)),
        "skills": len(assets.install_skills(root)),
        "cmds": len(assets.install_commands(root)),
        "rules": len(assets.install_rules(root)),
    }
    assets.install_agent_memory(root)
    scaffold = assets.install_scaffold(root)
    _report_init(hooks_dst, settings_path, len(copied), added, statusline, counts, scaffold)
    return 0


def _report_init(hooks_dst, settings_path, copied, added, statusline, counts, scaffold) -> None:
    """Print the install summary (split out to keep run_init under the line limit)."""
    sl = "installed (⚛ INERTIA forge)" if statusline else "already configured"
    print(f"inertia-forge: installed {copied} hook(s) into {hooks_dst}")
    print(f"inertia-forge: wired {added} new hook entr(y/ies) into {settings_path}")
    print(f"inertia-forge: statusLine {sl}")
    print(f"inertia-forge: installed {counts['agents']} agent(s) + {counts['skills']} skill doc(s)")
    print(f"inertia-forge: installed {counts['cmds']} slash command(s), {counts['rules']} rule doc(s)")
    print(f"inertia-forge: agent memory seeded; scaffolded {', '.join(scaffold) or '(nothing new)'}")
    print("Restart Claude Code (or reload settings) for the hooks to take effect.")
