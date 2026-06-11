"""Command policy — classify bash commands as allowed / review / blocked.

A deterministic safety layer the forge gate consults (`.forge/sandbox.yaml`):

  always_blocked   refuse outright (exit 2 at the gate)
  require_review   warn — risky, a human should confirm
  always_allowed   (reserved) explicitly safe

Defaults block only the catastrophic (rm -rf /, fork bomb, chmod -R 777, curl|sh)
and flag a few risky patterns for review — so it never fights normal dev work.
Customize by editing the YAML or `inertia-forge sandbox init`.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

SANDBOX = Path(".forge") / "sandbox.yaml"

_DEFAULT = {
    "always_blocked": [
        r"rm\s+-rf\s+(/|~|\$HOME)(\s|$)",   # wipe root / home
        r":\(\)\s*\{.*\|.*&\s*\}",           # fork bomb
        r"chmod\s+-R\s+777\s+/",             # world-writable root
        r"curl\s.+\|\s*(sudo\s+)?(ba)?sh",   # curl | sh
        r"dd\s+if=.+\s+of=/dev/(sd|nvme|disk)",
        r"mkfs\.",                            # format a filesystem
    ],
    "require_review": [
        r"\brm\s+-rf\b", r"git\s+reset\s+--hard", r"git\s+push\s+.*--force",
        r"\bDROP\s+TABLE\b", r"\bTRUNCATE\b", r"kubectl\s+delete",
    ],
    "always_allowed": [],
}


def load() -> dict:
    d: dict = {}
    if SANDBOX.exists():
        try:
            d = yaml.safe_load(SANDBOX.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            d = {}
    for k, v in _DEFAULT.items():
        d.setdefault(k, list(v))
    return d


def classify(command: str, policy: dict | None = None) -> str:
    policy = policy or load()
    for pat in policy.get("always_blocked", []):
        if re.search(pat, command):
            return "blocked"
    for pat in policy.get("require_review", []):
        if re.search(pat, command):
            return "review"
    return "allowed"


def run_sandbox(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge sandbox")
    sub = p.add_subparsers(dest="sub", required=True)
    sub.add_parser("status")
    sub.add_parser("init")
    ck = sub.add_parser("check"); ck.add_argument("command", nargs=argparse.REMAINDER)
    args = p.parse_args(argv)
    if args.sub == "init":
        SANDBOX.parent.mkdir(parents=True, exist_ok=True)
        SANDBOX.write_text(yaml.safe_dump(_DEFAULT, sort_keys=False), encoding="utf-8")
        print(f"wrote default command policy to {SANDBOX}")
        return 0
    if args.sub == "check":
        cmd = " ".join(args.command)
        tier = classify(cmd)
        print(f"{cmd!r}: {tier}")
        return 2 if tier == "blocked" else 0
    pol = load()
    print(f"command policy ({'custom' if SANDBOX.exists() else 'defaults'}):")
    print(f"  always_blocked: {len(pol['always_blocked'])} pattern(s)")
    print(f"  require_review: {len(pol['require_review'])} pattern(s)")
    return 0
