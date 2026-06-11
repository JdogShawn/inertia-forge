"""Project scaffolding — generate a forge-ready project layout. Zero LLM.

`template new <dir>` writes a complete starter: a skills file, a pre-commit
config wired to `inertia-forge check`, a CI workflow, src/tests layout, and a
README. Existing files are never overwritten.
"""
from __future__ import annotations

import argparse
from pathlib import Path

_SKILLS = """# Project skills (inertia-forge). Add your own gated workflows here.
reviewing_code:
  evidence_mode: stamped
  steps: [read, check_correctness, check_security, verdict]
  gates:
    check_correctness: blocking
    verdict: blocking
"""

_PRECOMMIT = """repos:
  - repo: https://github.com/JdogShawn/inertia-forge
    rev: v0.5.0
    hooks:
      - id: inertia-forge-check
      - id: inertia-forge-sweep
"""

_CI = """name: CI
on: [push, pull_request]
jobs:
  forge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install inertia-forge pytest
      - run: inertia-forge check . --tests tests/
"""

_GITIGNORE = "__pycache__/\n*.py[cod]\n.forge/\n.venv/\ndist/\n*.egg-info/\n"
_README = ("# Project\n\nForge-enforced. Run `inertia-forge check .` before "
           "committing; CI runs it too.\n")
_TEST = "def test_smoke():\n    assert True\n"

_FILES = {
    "forge_skills.yaml": _SKILLS,
    ".pre-commit-config.yaml": _PRECOMMIT,
    ".github/workflows/ci.yml": _CI,
    ".gitignore": _GITIGNORE,
    "README.md": _README,
    "src/__init__.py": "",
    "tests/test_smoke.py": _TEST,
}


def scaffold(dest: Path) -> tuple[list[str], list[str]]:
    """Write the template into dest. Returns (created, skipped-existing)."""
    created, skipped = [], []
    for rel, content in _FILES.items():
        path = dest / rel
        if path.exists():
            skipped.append(rel)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        created.append(rel)
    return created, skipped


def run_template(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge template")
    sub = p.add_subparsers(dest="sub", required=True)
    sub.add_parser("list")
    n = sub.add_parser("new"); n.add_argument("dir", nargs="?", default=".")
    args = p.parse_args(argv)
    if args.sub == "list":
        print("  default — forge-wired Python project (skills, pre-commit, CI, src/tests)")
        return 0
    created, skipped = scaffold(Path(args.dir))
    for rel in created:
        print(f"  + {rel}")
    for rel in skipped:
        print(f"  = {rel} (exists, kept)")
    print(f"scaffolded {len(created)} file(s) into {Path(args.dir).resolve()}")
    return 0
