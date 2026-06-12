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

A suite carries a name, optional description, suite-level ``tags`` and
``preconditions`` (steps that must pass or the whole suite is skipped), and
tagged scenarios. ``${VAR}`` is interpolated from the environment. Steps: ``run``
(+ expect_exit/expect_contains/expect_not_contains), ``file_exists``,
``file_contains``. Each scenario gets a verdict — passed / failed / skipped.

Subcommands::

    qc <suite>          run (default); --tags / --skip-tags filter scenarios
    qc validate <s>     schema check only, no execution
    qc list [dir]       discover *.qc.yaml suites (--tags to filter)
    qc init             scaffold .forge/qc/ with an example suite

Exits 1 on any failed scenario. Deterministic — every step is a forge command or
a file check; no model, no browser.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import shlex
from pathlib import Path

import yaml

from inertia_forge import qc_suite


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


def check_preconditions(suite: dict) -> list[str]:
    """Failure details for any suite-level precondition step (empty = all pass)."""
    fails = []
    for step in suite.get("preconditions", []):
        ok, detail = _run_step(step)
        if not ok:
            fails.append(detail)
    return fails


def run_suite(suite: dict, only_tags: list[str] | None = None,
              skip_tags: list[str] | None = None) -> list[tuple[str, str, list[str]]]:
    """[(scenario_name, verdict, failures)]; verdict ∈ passed / failed / skipped."""
    results = []
    for sc in suite.get("scenarios", []):
        name = sc.get("name", "(unnamed)")
        sc_tags = set(sc.get("tags", []))
        if (skip_tags and sc_tags & set(skip_tags)) or (only_tags and not sc_tags & set(only_tags)):
            results.append((name, "skipped", []))
            continue
        failures = []
        for step in sc.get("steps", []):
            ok, detail = _run_step(step)
            if not ok:
                failures.append(detail)
        results.append((name, "passed" if not failures else "failed", failures))
    return results


def _emit_telemetry(results: list[tuple[str, str, list[str]]], path: Path) -> None:
    from inertia_forge import telemetry
    ran = [r for r in results if r[1] != "skipped"]
    passed = sum(1 for _, v, _ in ran if v == "passed")
    if ran:
        telemetry.record("qc", "qc_pass_rate", round(100 * passed / len(ran), 1),
                         {"passed": passed, "total": len(ran), "suite": str(path)})
    for name, verdict, _ in ran:  # per-scenario history → flaky detection
        telemetry.record("qc_scenario", name, 1.0 if verdict == "passed" else 0.0, {"suite": str(path)})


def _report(results: list[tuple[str, str, list[str]]]) -> int:
    from inertia_forge.glyphs import seal
    glyph = {"passed": "ok", "failed": "error", "skipped": "info"}
    for name, verdict, failures in results:
        print(f"{seal(glyph[verdict])} {name} ({verdict})")
        for detail in failures:
            print(f"    - {detail}")
    p = sum(1 for _, v, _ in results if v == "passed")
    f = sum(1 for _, v, _ in results if v == "failed")
    s = sum(1 for _, v, _ in results if v == "skipped")
    print(f"\n{p} passed, {f} failed, {s} skipped")
    return 1 if f else 0


def _cmd_run(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge qc")
    p.add_argument("suite")
    p.add_argument("--tags", nargs="*", default=None, help="run only scenarios with these tags")
    p.add_argument("--skip-tags", nargs="*", default=None, help="skip scenarios with these tags")
    args = p.parse_args(argv)
    path = Path(args.suite)
    if not path.is_file():
        print(f"QC suite not found: {path}")
        return 1
    try:
        suite, unresolved = qc_suite.load(path)
    except yaml.YAMLError as e:
        print(f"invalid QC suite: {e}")
        return 1
    if errors := qc_suite.validate(suite):
        for e in errors:
            print(f"{seal('error')} {e}")
        return 1
    if unresolved:
        print(f"{seal('warn')} unresolved variable(s): {', '.join(sorted(unresolved))}")
    if pre := check_preconditions(suite):
        print(f"{seal('warn')} precondition failed — suite skipped: {pre[0]}")
        return 1
    results = run_suite(suite, args.tags, args.skip_tags)
    if not results:
        print("(no scenarios)")
        return 0
    _emit_telemetry(results, path)
    return _report(results)


def _cmd_validate(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge qc validate")
    p.add_argument("suite")
    args = p.parse_args(argv)
    path = Path(args.suite)
    if not path.is_file():
        print(f"QC suite not found: {path}")
        return 1
    try:
        suite, _ = qc_suite.load(path)
    except yaml.YAMLError as e:
        print(f"{seal('error')} parse error: {e}")
        return 1
    errors = qc_suite.validate(suite)
    for e in errors:
        print(f"{seal('error')} {e}")
    if errors:
        return 1
    print(f"{seal('ok')} {path.name} valid ({len(suite.get('scenarios', []))} scenario(s))")
    return 0


def _cmd_list(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge qc list")
    p.add_argument("dir", nargs="?", default=".")
    p.add_argument("--tags", nargs="*", default=None)
    args = p.parse_args(argv)
    suites = qc_suite.discover(Path(args.dir), args.tags)
    if not suites:
        print("(no .qc.yaml suites found)")
        return 0
    for s in suites:
        print(f"  {s}")
    return 0


def run_qc(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    if argv and argv[0] in ("run", "validate", "list", "init"):
        sub, rest = argv[0], argv[1:]
    else:
        sub, rest = "run", argv
    if sub == "init":
        print(f"{seal('ok')} scaffolded {qc_suite.scaffold()}")
        return 0
    if sub == "validate":
        return _cmd_validate(rest)
    if sub == "list":
        return _cmd_list(rest)
    return _cmd_run(rest)
