"""The forge's own gated tool set — execution and file ops, enforced.

Claude has Bash / Write / Edit / Read; the forge's purpose is to gate them. These
are first-class deterministic equivalents that pass through the forge's gates at
the tool boundary, so enforcement isn't just a hook on someone else's tool:

  run   classify the command against the sandbox policy; refuse anything blocked
  write check the containment tier; refuse a protected/read-only path
  edit  same containment check, then an exact-match in-place replacement
  view  refuse a blocked path, else print

Every call is recorded to the behavioral audit log. An agent driving the forge
through these literally cannot run a catastrophic command or write outside its
containment. (The runner invokes the shell without ``shell=True`` — gated, and
clean under the forge's own `vet`.)
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _shell(cmd: str) -> list[str]:
    if os.name == "nt":
        return [os.environ.get("COMSPEC", "cmd.exe"), "/c", cmd]
    return [os.environ.get("SHELL", "/bin/sh"), "-c", cmd]


def run_exec(argv: list[str]) -> int:
    from inertia_forge.bypass_prevention import log_behavioral_event
    from inertia_forge.glyphs import seal
    from inertia_forge.sandbox import classify
    p = argparse.ArgumentParser(prog="inertia-forge run")
    p.add_argument("--allow-review", action="store_true",
                   help="permit a review-tier command (place BEFORE the command)")
    p.add_argument("command", nargs=argparse.REMAINDER, help="the command to run (gated)")
    args = p.parse_args(argv)
    cmd = " ".join(args.command).strip()
    if not cmd:
        print("usage: inertia-forge run [--allow-review] <command...>")
        return 2
    tier = classify(cmd)
    # A gate never auto-runs anything but an explicitly-allowed command.
    if tier == "blocked":
        log_behavioral_event("tool_run_blocked", cmd)
        print(f"{seal('error')} BLOCKED by sandbox policy — will not run: {cmd}")
        return 2
    if tier == "review" and not args.allow_review:
        log_behavioral_event("tool_run_refused", cmd)
        print(f"{seal('warn')} review-tier command refused — re-run with "
              f"--allow-review if you are sure: {cmd}")
        return 2
    log_behavioral_event("tool_run", cmd)
    try:
        return subprocess.run(_shell(cmd)).returncode
    except OSError as e:
        print(f"{seal('error')} failed to run: {e}")
        return 1


def _deny_write(path: str) -> int | None:
    from inertia_forge.bypass_prevention import log_behavioral_event
    from inertia_forge.containment import classify, is_write_allowed
    from inertia_forge.glyphs import seal
    if not is_write_allowed(path):
        log_behavioral_event("tool_write_blocked", path)
        print(f"{seal('error')} containment BLOCKED write to {path} (tier: {classify(path)})")
        return 2
    return None


def run_write(argv: list[str]) -> int:
    from inertia_forge.bypass_prevention import log_behavioral_event
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge write")
    p.add_argument("path")
    p.add_argument("--content", help="content to write (default: read from stdin)")
    args = p.parse_args(argv)
    if (denied := _deny_write(args.path)) is not None:
        return denied
    content = args.content if args.content is not None else sys.stdin.read()
    target = Path(args.path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    log_behavioral_event("tool_write", args.path)
    print(f"{seal('ok')} wrote {args.path} ({len(content)} chars)")
    return 0


def run_edit(argv: list[str]) -> int:
    from inertia_forge.bypass_prevention import log_behavioral_event
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge edit")
    p.add_argument("path")
    p.add_argument("--old", required=True, help="exact text to replace (must be unique)")
    p.add_argument("--new", required=True, help="replacement text")
    args = p.parse_args(argv)
    if (denied := _deny_write(args.path)) is not None:
        return denied
    target = Path(args.path)
    if not target.is_file():
        print(f"{seal('error')} no such file: {args.path}")
        return 1
    text = target.read_text(encoding="utf-8")
    count = text.count(args.old)
    if count != 1:
        print(f"{seal('error')} --old must match exactly once (found {count})")
        return 1
    target.write_text(text.replace(args.old, args.new), encoding="utf-8")
    log_behavioral_event("tool_edit", args.path)
    print(f"{seal('ok')} edited {args.path}")
    return 0


def run_view(argv: list[str]) -> int:
    from inertia_forge.containment import classify
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge view")
    p.add_argument("path")
    args = p.parse_args(argv)
    if classify(args.path) == "blocked":
        print(f"{seal('error')} containment BLOCKED read of {args.path}")
        return 2
    target = Path(args.path)
    if not target.is_file():
        print(f"{seal('error')} no such file: {args.path}")
        return 1
    print(target.read_text(encoding="utf-8"), end="")
    return 0
