"""Containment — INERTIA's deterministic file-access tiers.

A contained session restricts which paths an agent may modify. Three tiers,
matched most-restrictive-first against forward-slash globs:

  blocked    no access (write blocked; read discouraged)
  readonly   may read, may NOT write
  readwrite  full access (the default for anything unmatched)

Config lives in `.forge/containment.json`::

    {"active": true,
     "blocked":  [".env", "*.pem", "secrets/*"],
     "readonly": ["CLAUDE.md", ".github/*"]}

When inactive (default), nothing is restricted. Enforcement is wired through a
PreToolUse(Edit|Write) hook (see hookutil.cmd_contain) — deterministic, no LLM.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path

CONTAINMENT = Path(".forge") / "containment.json"


def load() -> dict:
    if CONTAINMENT.exists():
        try:
            d = json.loads(CONTAINMENT.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            d = {}
    else:
        d = {}
    d.setdefault("active", False)
    d.setdefault("blocked", [])
    d.setdefault("readonly", [])
    return d


def save(d: dict) -> None:
    CONTAINMENT.parent.mkdir(parents=True, exist_ok=True)
    CONTAINMENT.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _matches(path: str, globs: list[str]) -> bool:
    norm = path.replace("\\", "/")
    if norm.startswith("./"):   # strip a leading "./" PREFIX (not via lstrip,
        norm = norm[2:]         # which would eat the dot of a dotfile like .env)
    base = norm.rsplit("/", 1)[-1]
    return any(fnmatch.fnmatch(norm, g) or fnmatch.fnmatch(base, g) for g in globs)


def classify(path: str, cfg: dict | None = None) -> str:
    """Return the tier for a path: blocked / readonly / readwrite."""
    cfg = cfg or load()
    if _matches(path, cfg["blocked"]):
        return "blocked"
    if _matches(path, cfg["readonly"]):
        return "readonly"
    return "readwrite"


def is_write_allowed(path: str, cfg: dict | None = None) -> bool:
    """True if writing `path` is permitted (always True when inactive)."""
    cfg = cfg or load()
    if not cfg.get("active"):
        return True
    return classify(path, cfg) == "readwrite"


def run_contain(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge contain")
    sub = p.add_subparsers(dest="sub", required=True)
    sub.add_parser("status")
    sub.add_parser("on")
    sub.add_parser("off")
    st = sub.add_parser("set")
    st.add_argument("--blocked", action="append", default=[])
    st.add_argument("--readonly", action="append", default=[])
    ck = sub.add_parser("check")
    ck.add_argument("path")
    args = p.parse_args(argv)
    cfg = load()

    if args.sub in ("on", "off"):
        cfg["active"] = args.sub == "on"
        save(cfg)
        print(f"containment {'ACTIVE' if cfg['active'] else 'off'}")
        return 0
    if args.sub == "set":
        cfg["blocked"] = sorted(set(cfg["blocked"]) | set(args.blocked))
        cfg["readonly"] = sorted(set(cfg["readonly"]) | set(args.readonly))
        save(cfg)
        print(f"blocked={cfg['blocked']}  readonly={cfg['readonly']}")
        return 0
    if args.sub == "check":
        tier = classify(args.path, cfg)
        print(f"{args.path}: {tier} (write {'allowed' if is_write_allowed(args.path, cfg) else 'BLOCKED'})")
        return 0
    print(f"containment: {'ACTIVE' if cfg['active'] else 'off'}")
    print(f"  blocked:  {cfg['blocked'] or '(none)'}")
    print(f"  readonly: {cfg['readonly'] or '(none)'}")
    return 0
