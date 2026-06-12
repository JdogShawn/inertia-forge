"""Declarative QC runner — acceptance scenarios as data, not code.

A QC suite (``.qc.yaml``) lists scenarios, each a sequence of steps that exercise
the project's CLI and filesystem and assert on the result:

    name: forge smoke
    scenarios:
      - name: status works
        steps:
          - run: status
            expect_exit: 0
          - run: arch src/
            expect_contains: "no findings"
      - name: vet blocks a vuln
        steps:
          - run: vet tests/fixtures/bad.py
            expect_exit: 1
      - name: artifact present
        steps:
          - file_exists: README.md
          - file_contains: { path: pyproject.toml, text: inertia-forge }

`qc <suite.yaml>` runs them all and reports pass/fail per scenario, exiting 1 on
any failure. Deterministic — every step is a forge command or a file check; no
model, no browser.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import shlex
from pathlib import Path

import yaml


def _run_command_step(step: dict) -> tuple[bool, str]:
    from inertia_forge.cli import main
    argv = shlex.split(step["run"])
    buf = io.StringIO()
    code: int = 0
    with contextlib.redirect_stdout(buf):
        try:
            code = main(argv) or 0
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 0
        except Exception as e:  # a crashing command is a failed step, not a crash
            return False, f"run '{step['run']}' raised {type(e).__name__}: {e}"
    out = buf.getvalue()
    label = f"run '{step['run']}'"
    if "expect_exit" in step and code != step["expect_exit"]:
        return False, f"{label} exit {code} != {step['expect_exit']}"
    if "expect_contains" in step and step["expect_contains"] not in out:
        return False, f"{label} output missing {step['expect_contains']!r}"
    if "expect_not_contains" in step and step["expect_not_contains"] in out:
        return False, f"{label} output contains forbidden {step['expect_not_contains']!r}"
    return True, label


def _run_step(step: dict) -> tuple[bool, str]:
    if "run" in step:
        return _run_command_step(step)
    if "file_exists" in step:
        return Path(step["file_exists"]).exists(), f"file_exists {step['file_exists']}"
    if "file_contains" in step:
        spec = step["file_contains"]
        p = Path(spec["path"])
        text = p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""
        return spec["text"] in text, f"file_contains {spec['path']}"
    return False, f"unknown step: {sorted(step)}"


def run_suite(suite: dict) -> list[tuple[str, bool, list[str]]]:
    """[(scenario_name, passed, [failure_details])] for every scenario."""
    results = []
    for sc in suite.get("scenarios", []):
        failures = []
        for step in sc.get("steps", []):
            ok, detail = _run_step(step)
            if not ok:
                failures.append(detail)
        results.append((sc.get("name", "(unnamed)"), not failures, failures))
    return results


def run_qc(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge qc")
    p.add_argument("suite", help="path to a .qc.yaml suite")
    args = p.parse_args(argv)
    path = Path(args.suite)
    if not path.is_file():
        print(f"QC suite not found: {path}")
        return 1
    try:
        suite = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        print(f"invalid QC suite: {e}")
        return 1
    results = run_suite(suite)
    if not results:
        print("(no scenarios)")
        return 0
    passed = sum(1 for _, ok, _ in results if ok)
    from inertia_forge import telemetry
    telemetry.record("qc", "qc_pass_rate",
                     round(100 * passed / len(results), 1),
                     {"passed": passed, "total": len(results), "suite": str(path)})
    for sc_name, sc_ok, _ in results:  # per-scenario history → flaky detection
        telemetry.record("qc_scenario", sc_name, 1.0 if sc_ok else 0.0, {"suite": str(path)})
    for name, ok, failures in results:
        print(f"{seal('ok' if ok else 'error')} {name}")
        for detail in failures:
            print(f"    - {detail}")
    print(f"\n{passed}/{len(results)} scenario(s) passed")
    return 0 if passed == len(results) else 1
