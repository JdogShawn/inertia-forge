"""`inertia-forge banner` / `logo` — show the brand marks.

  inertia-forge banner              full atom + wordmark + tagline + vow
  inertia-forge logo [--variant V]  just the atom (full / compact / tiny)
"""
from __future__ import annotations

import argparse

from inertia_forge import __version__
from inertia_forge.brand import banner, logo


def run_banner(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge banner")
    p.add_argument("--subtitle", default="", help="override the tagline line")
    args = p.parse_args(argv)
    print(banner(version=__version__, subtitle=args.subtitle))
    return 0


def run_logo(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge logo")
    p.add_argument("--variant", choices=("full", "compact", "tiny"), default="full")
    args = p.parse_args(argv)
    print("\n".join(logo(args.variant)))
    return 0
