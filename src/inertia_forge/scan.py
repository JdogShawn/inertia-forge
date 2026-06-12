"""Full quality scan — the whole deterministic battery in one pass.

Runs every standalone analyzer over the source tree and prints a single
ship / no-ship verdict: arch, check (arch+secrets), vet, imports, xref, and
dead-code are *gating* (a finding fails the scan); sweep and review are advisory.
With ``--snapshot`` it also records a telemetry snapshot. The one command the
Crucible QC agent (and CI) runs instead of a dozen.
"""
from __future__ import annotations

import argparse
import contextlib
import io

# (label, argv-builder, gating?) — gating means a nonzero exit fails the scan.
_BATTERY = [
    ("arch", lambda p: ["arch", p], True),
    ("check (arch+secrets)", lambda p: ["check", p], True),
    ("vet (insecure code)", lambda p: ["vet", p], True),
    ("imports (cycles)", lambda p: ["imports", p], True),
    ("xref (dangling refs)", lambda p: ["xref", p], True),
    ("dead-code (exports)", lambda p: ["dead-code", p], True),
    ("sweep (unused imports)", lambda p: ["sweep", p], False),
    ("review (smells)", lambda p: ["review", p], False),
]


def battery(path: str) -> list[tuple[str, int, bool]]:
    """[(label, exit_code, gating)] from running each analyzer, output suppressed."""
    from inertia_forge.cli import main as forge_main
    out = []
    for label, build, gating in _BATTERY:
        buf = io.StringIO()
        rc = 0
        with contextlib.redirect_stdout(buf):
            with contextlib.suppress(SystemExit):
                rc = forge_main(build(path)) or 0
        out.append((label, rc, gating))
    return out


def run_scan(argv: list[str]) -> int:
    from inertia_forge.cli import main as forge_main
    from inertia_forge.glyphs import g, seal
    from inertia_forge.palette import paint
    p = argparse.ArgumentParser(prog="inertia-forge scan")
    p.add_argument("path", nargs="?", default="src", help="source tree to scan")
    p.add_argument("--snapshot", action="store_true", help="also record a telemetry snapshot")
    args = p.parse_args(argv)

    results = battery(args.path)
    fails = 0
    for label, rc, gating in results:
        ok = rc == 0
        if not ok and gating:
            fails += 1
        kind = "ok" if ok else ("error" if gating else "warn")
        verdict = "pass" if ok else ("FAIL" if gating else "findings")
        print(f"  {seal(kind)} {paint(label.ljust(24), 'text')} {paint(verdict, kind if kind != 'ok' else 'success')}")
    if args.snapshot:
        with contextlib.redirect_stdout(io.StringIO()):
            forge_main(["telemetry", "snapshot", "--path", args.path])
        print(f"  {seal('info')} {paint('telemetry'.ljust(24), 'text')} snapshot recorded")
    print(f"\n{seal('error' if fails else 'ok')} "
          f"{'NOT READY' if fails else 'clean'} {g('dot')} {fails} gating failure(s)")
    return 1 if fails else 0
