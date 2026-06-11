"""Forge configuration — `.forge/config.json` (get / set / unset / list).

Typed, persistent project settings other commands read (e.g. default target,
default metrics model, base branch). Values are coerced to bool/int/float when
they look like one, else kept as strings.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

CONFIG = Path(".forge") / "config.json"


def load() -> dict:
    if CONFIG.exists():
        try:
            return json.loads(CONFIG.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def get(key: str, default=None):
    return load().get(key, default)


def set_value(key: str, value) -> None:
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    data = load()
    data[key] = value
    CONFIG.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def unset(key: str) -> bool:
    data = load()
    if key not in data:
        return False
    del data[key]
    CONFIG.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return True


def _coerce(raw: str):
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    for cast in (int, float):
        try:
            return cast(raw)
        except ValueError:
            continue
    return raw


def run_config(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge config")
    sub = p.add_subparsers(dest="sub", required=True)
    g = sub.add_parser("get"); g.add_argument("key")
    s = sub.add_parser("set"); s.add_argument("key"); s.add_argument("value")
    u = sub.add_parser("unset"); u.add_argument("key")
    sub.add_parser("list")
    args = p.parse_args(argv)
    if args.sub == "get":
        val = get(args.key)
        print("" if val is None else val)
        return 0 if val is not None else 1
    if args.sub == "set":
        set_value(args.key, _coerce(args.value))
        print(f"{args.key} = {get(args.key)!r}")
        return 0
    if args.sub == "unset":
        print(f"unset {args.key}" if unset(args.key) else f"{args.key} not set")
        return 0
    data = load()
    if not data:
        print("(no config)")
    for k in sorted(data):
        print(f"  {k} = {data[k]!r}")
    return 0
