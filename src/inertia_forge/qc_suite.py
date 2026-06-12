"""QC suite schema — load, validate, interpolate, discover, scaffold.

The deterministic half of a QC suite system: the YAML schema (name, description,
tags, preconditions, scenarios → steps), required-field validation, ``${VAR}``
interpolation from the environment with unresolved-variable detection, suite
discovery with tag filtering, and a scaffold. Kept separate from the runner so
each file stays small.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import yaml

VAR = re.compile(r"\$\{(\w+)\}")
QC_DIR = Path(".forge") / "qc"
_STEP_KINDS = ("run", "file_exists", "file_contains")


def interpolate(obj: object) -> tuple[object, set[str]]:
    """Replace ``${VAR}`` with os.environ; return (resolved_obj, unresolved_names)."""
    unresolved: set[str] = set()

    def walk(x: object) -> object:
        if isinstance(x, str):
            def sub(m: re.Match) -> str:
                val = os.environ.get(m.group(1))
                if val is None:
                    unresolved.add(m.group(1))
                    return m.group(0)
                return val
            return VAR.sub(sub, x)
        if isinstance(x, list):
            return [walk(i) for i in x]
        if isinstance(x, dict):
            return {k: walk(v) for k, v in x.items()}
        return x

    return walk(obj), unresolved


def validate(suite: dict) -> list[str]:
    """Required-field errors for a suite dict (empty list = valid)."""
    errors: list[str] = []
    scenarios = suite.get("scenarios")
    if not scenarios:
        errors.append("missing or empty required field 'scenarios'")
        return errors
    for i, sc in enumerate(scenarios, 1):
        label = sc.get("name", f"#{i}")
        if not sc.get("name"):
            errors.append(f"scenario {label}: missing 'name'")
        if not sc.get("steps"):
            errors.append(f"scenario {label}: no steps")
        for step in sc.get("steps", []):
            if not isinstance(step, dict) or not (set(step) & set(_STEP_KINDS)):
                errors.append(f"scenario {label}: unknown step {sorted(step) if isinstance(step, dict) else step}")
    return errors


def load(path: Path) -> tuple[dict, set[str]]:
    """Parse + interpolate a suite file. Returns (suite, unresolved_vars)."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    resolved, unresolved = interpolate(raw)
    return resolved, unresolved


def discover(root: Path, tags: list[str] | None = None) -> list[Path]:
    """`*.qc.yaml` suites under *root*, optionally filtered to those whose
    suite-level tags include any of *tags*."""
    suites = sorted(p for p in root.rglob("*.qc.yaml") if "__pycache__" not in p.parts)
    if not tags:
        return suites
    out = []
    for p in suites:
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        if set(data.get("tags", [])) & set(tags):
            out.append(p)
    return out


def scaffold() -> Path:
    """Create .forge/qc/ with an example suite. Returns the example's path."""
    QC_DIR.mkdir(parents=True, exist_ok=True)
    example = QC_DIR / "example.qc.yaml"
    if not example.exists():
        example.write_text(
            "name: example smoke\n"
            "description: a starter QC suite\n"
            "tags: [smoke]\n"
            "scenarios:\n"
            "  - name: project has a readme\n"
            "    tags: [docs]\n"
            "    steps:\n"
            "      - file_exists: README.md\n"
            "  - name: status command works\n"
            "    steps:\n"
            "      - run: status\n"
            "        expect_exit: 0\n", encoding="utf-8")
    return example
