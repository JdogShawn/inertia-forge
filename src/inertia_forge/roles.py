"""File role detector — classify a path by architectural role, cheaply.

Path-pattern detection, first match wins: test, doc, config, data, script, cli,
init, source. Underpins targeted-test selection and arch's test-aware limits —
pure path inspection, no file read. `role <path>...` prints the classification.
"""
from __future__ import annotations

from pathlib import Path

ROLES = ("test", "doc", "config", "data", "script", "cli", "init", "source")

_CONFIG_NAMES = {"setup.py", "conftest.py", "noxfile.py"}
_CONFIG_SUFFIX = {".toml", ".cfg", ".ini", ".yaml", ".yml", ".json"}
_DOC_SUFFIX = {".md", ".rst", ".txt", ".adoc"}
_DATA_SUFFIX = {".csv", ".jsonl", ".parquet", ".sqlite", ".db", ".ndjson"}


def detect(path: str | Path) -> str:
    """Return the architectural role of *path* (first matching rule wins)."""
    p = Path(path)
    name = p.name.lower()
    parts = {x.lower() for x in p.parts}
    if name.startswith("test_") or name.endswith("_test.py") or {"test", "tests"} & parts:
        return "test"
    if p.suffix.lower() in _DOC_SUFFIX:
        return "doc"
    if name in _CONFIG_NAMES or p.suffix.lower() in _CONFIG_SUFFIX:
        return "config"
    if p.suffix.lower() in _DATA_SUFFIX:
        return "data"
    if "scripts" in parts:
        return "script"
    if name in ("cli.py", "__main__.py") or name.endswith("_cli.py"):
        return "cli"
    if name == "__init__.py":
        return "init"
    return "source"


def detect_batch(paths: list[str | Path]) -> dict[str, str]:
    return {str(p): detect(p) for p in paths}


def run_role(argv: list[str]) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="inertia-forge role")
    parser.add_argument("paths", nargs="+", help="files to classify")
    args = parser.parse_args(argv)
    from inertia_forge.palette import paint
    role_color = {"test": "go", "config": "warn", "doc": "muted",
                  "data": "info", "cli": "accent", "source": "text"}
    for path in args.paths:
        r = detect(path)
        print(f"  {paint(r.ljust(7), role_color.get(r, 'text'))}  {path}")
    return 0
