"""Project health report — one markdown page unifying the deterministic signals.

Aggregates the forge's analyzers and telemetry into a single paste-able report:
the scan-battery verdict per analyzer, code-quality numbers (docstring / type-hint
%, dead symbols, over-complexity, coverage), and task progress. `report` prints
markdown — redirect to a file for a CI artifact or hand it to an LLM.
Deterministic; ASCII-clean.
"""
from __future__ import annotations

import argparse


def build_report(path: str) -> str:
    from inertia_forge import __version__, tasks as tk
    from inertia_forge.scan import battery
    from inertia_forge.telemetry import snapshot_metrics

    lines = [f"# Project Health Report (inertia-forge v{__version__})", ""]

    results = battery(path)
    fails = sum(1 for _, rc, gating in results if rc != 0 and gating)
    lines += [f"**Quality battery:** {'PASS' if not fails else f'{fails} gating failure(s)'}",
              "", "| analyzer | result |", "|---|---|"]
    for label, rc, gating in results:
        verdict = "pass" if rc == 0 else ("**FAIL**" if gating else "findings")
        lines.append(f"| {label} | {verdict} |")

    metrics = snapshot_metrics(path)
    if metrics:
        lines += ["", "## Code quality", "", "| metric | value |", "|---|---|"]
        for k, v in metrics.items():
            lines.append(f"| {k} | {v:g} |")

    tasks = tk.list_tasks()
    if tasks:
        done = sum(1 for x in tasks if x["status"] == "done")
        ac_met = sum(1 for x in tasks for c in x["acceptance_criteria"] if c["done"])
        ac_tot = sum(len(x["acceptance_criteria"]) for x in tasks)
        lines += ["", "## Tasks", "",
                  f"- {done}/{len(tasks)} tasks done",
                  f"- {ac_met}/{ac_tot} acceptance criteria met"]

    return "\n".join(lines) + "\n"


def run_report(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge report")
    p.add_argument("--path", default="src", help="source tree to report on")
    args = p.parse_args(argv)
    print(build_report(args.path))
    return 0
