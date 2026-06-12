"""Configuration presets — named archetypes that bootstrap forge config fast.

Each preset is a bundle of known config keys for a project shape. `preset list`
shows them, `preset show <name>` previews the keys, `preset apply <name>` writes
them through the config store. Deterministic and offline — no templates server.
"""
from __future__ import annotations

import argparse

PRESETS: dict[str, dict[str, str]] = {
    "library": {"target": "src/", "base_branch": "main"},
    "service": {"target": "app/", "base_branch": "main"},
    "cli":     {"target": "src/", "base_branch": "main"},
    "data":    {"target": "pipelines/", "base_branch": "main"},
}


def run_preset(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge preset")
    sub = p.add_subparsers(dest="sub", required=True)
    sub.add_parser("list", help="list available presets")
    sh = sub.add_parser("show", help="preview a preset's keys"); sh.add_argument("name")
    ap = sub.add_parser("apply", help="write a preset into .forge/config.json"); ap.add_argument("name")
    args = p.parse_args(argv)

    if args.sub == "list":
        for name in sorted(PRESETS):
            keys = ", ".join(f"{k}={v}" for k, v in PRESETS[name].items())
            print(f"  {name:10} {keys}")
        return 0

    preset = PRESETS.get(args.name)
    if preset is None:
        print(f"unknown preset: {args.name} (try: {', '.join(sorted(PRESETS))})")
        return 1
    if args.sub == "show":
        for k, v in preset.items():
            print(f"  {k} = {v}")
        return 0
    from inertia_forge import config
    for k, v in preset.items():
        config.set_value(k, v)
    print(f"applied preset '{args.name}' ({len(preset)} key(s)) → .forge/config.json")
    return 0
