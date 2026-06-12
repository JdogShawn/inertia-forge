"""Policy lint — flag the function calls your project has banned.

Architectural policy beyond `vet`'s fixed security rules: list the calls you
don't want in ``.forge/banned.txt`` — one dotted name per line, optional
``# reason`` — e.g. ``subprocess.run  # use utils.sh`` or ``print  # libraries
log, not print``. `policy` AST-scans for them (matching the full dotted name or
the bare callee) and reports each site. Opt-in (no file → nothing flagged),
deterministic, with a per-line ``# noqa: policy`` escape.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

BANNED_FILE = Path(".forge") / "banned.txt"


def load_banned() -> dict[str, str]:
    """{dotted_name: reason} from .forge/banned.txt; {} if absent."""
    if not BANNED_FILE.exists():
        return {}
    out: dict[str, str] = {}
    for line in BANNED_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, _, reason = line.partition("#")
        if name.strip():
            out[name.strip()] = reason.strip()
    return out


def _call_name(node: ast.Call) -> str:
    """Dotted name of a call's callee: subprocess.run / os.system / print."""
    f: ast.AST = node.func
    parts: list[str] = []
    while isinstance(f, ast.Attribute):
        parts.append(f.attr)
        f = f.value
    if isinstance(f, ast.Name):
        parts.append(f.id)
    return ".".join(reversed(parts)) if parts else ""


def scan_file(path: str | Path, banned: dict[str, str]) -> list[tuple[str, int, str, str]]:
    """[(file, line, banned_name, reason)] for each banned call site in a .py file."""
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text, filename=str(p))
    except (OSError, SyntaxError):
        return []
    lines = text.splitlines()
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        if not name:
            continue
        hit = name if name in banned else (name.rsplit(".", 1)[-1] if name.rsplit(".", 1)[-1] in banned else None)
        if hit is None:
            continue
        src_line = lines[node.lineno - 1] if node.lineno - 1 < len(lines) else ""
        if "# noqa: policy" in src_line:
            continue
        out.append((str(p), node.lineno, hit, banned[hit]))
    return out


def run_policy(argv: list[str]) -> int:
    from inertia_forge.glyphs import seal
    from inertia_forge.palette import paint
    p = argparse.ArgumentParser(prog="inertia-forge policy")
    p.add_argument("path", nargs="?", default="src", help="file or dir to scan")
    args = p.parse_args(argv)
    banned = load_banned()
    if not banned:
        print(f"{seal('ok')} no policy bans configured (.forge/banned.txt)")
        return 0
    target = Path(args.path)
    files = ([f for f in target.rglob("*.py") if "__pycache__" not in f.parts]
             if target.is_dir() else [target])
    findings = [f for file in files for f in scan_file(file, banned)]
    if not findings:
        print(f"{seal('ok')} no banned calls ({len(banned)} rule(s))")
        return 0
    for path, ln, name, reason in findings:
        suffix = f" — {reason}" if reason else ""
        print(f"  {paint('[P1]', 'error')} {paint(name + '()', 'error')}{suffix} ({path}:{ln})")
    print(f"\n{seal('error')} {len(findings)} banned call(s)")
    return 1
