"""Insecure-code vetting — deterministic detection of dangerous patterns.

A dependency-free "bandit-lite": AST-walks Python for code that is almost never
safe — ``eval()``/``exec()``, ``subprocess(..., shell=True)``, ``os.system`` /
``os.popen``, untrusted ``pickle.load``, ``yaml.load`` without a safe Loader, and
weak hashes (md5/sha1) — plus a regex pass for SQL built by f-string. Because
the structural checks are AST-based, a mention in a string or comment doesn't
false-positive. eval/exec/shell/SQL are P1; the rest are advisory P2. `vet`
scans a path or the git-changed set and exits 1 on any P1.
"""
from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

_SQL = re.compile(r'''f["'].*\b(SELECT|INSERT|UPDATE|DELETE)\b.*\{''', re.IGNORECASE)


def _v(sev: str, path: Path, line: int, msg: str) -> dict:
    return {"severity": sev, "message": f"{path}:{line} {msg}"}


def _vet_call(node: ast.Call, path: Path) -> list[dict]:
    f, line = node.func, node.lineno
    if isinstance(f, ast.Name) and f.id in ("eval", "exec"):
        return [_v("P1", path, line, f"{f.id}() — arbitrary code execution")]
    if isinstance(f, ast.Attribute):
        attr = f.attr
        mod = f.value.id if isinstance(f.value, ast.Name) else ""
        if mod == "os" and attr in ("system", "popen"):
            return [_v("P2", path, line, f"os.{attr}() — prefer subprocess without a shell")]
        if mod == "pickle" and attr in ("load", "loads"):
            return [_v("P2", path, line, f"pickle.{attr}() — untrusted deserialization risk")]
        if mod == "yaml" and attr == "load" and not any(k.arg == "Loader" for k in node.keywords):
            return [_v("P2", path, line, "yaml.load() without Loader — use yaml.safe_load")]
        if mod == "hashlib" and attr in ("md5", "sha1"):
            return [_v("P2", path, line, f"hashlib.{attr}() — weak hash (advisory)")]
    for k in node.keywords:
        if k.arg == "shell" and isinstance(k.value, ast.Constant) and k.value.value is True:
            return [_v("P1", path, line, "shell=True — command injection risk")]
    return []


def vet_file(path: str | Path) -> list[dict]:
    """Every insecure-pattern finding in a single Python file."""
    p = Path(path)
    if p.suffix != ".py":
        return []
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text, filename=str(p))
    except (OSError, SyntaxError):
        return []
    findings: list[dict] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            findings += _vet_call(node, p)
    for i, line in enumerate(text.splitlines(), 1):
        if _SQL.search(line):
            findings.append(_v("P1", p, i, "SQL built with an f-string — injection risk"))
    return findings


def _collect(path: str | None, since: str) -> list[Path]:
    if path:
        p = Path(path)
        if p.is_dir():
            return [f for f in p.rglob("*.py") if "__pycache__" not in f.parts]
        return [p]
    from inertia_forge.targeted import git_changed
    return [Path(f) for f in git_changed(Path("."), since) if Path(f).suffix == ".py"]


def run_vet(argv: list[str]) -> int:
    from inertia_forge.glyphs import g, seal
    from inertia_forge.palette import paint
    p = argparse.ArgumentParser(prog="inertia-forge vet")
    p.add_argument("path", nargs="?", help="file/dir to vet (default: git-changed)")
    p.add_argument("--since", default="HEAD", help="git ref to diff against")
    args = p.parse_args(argv)
    findings: list[dict] = []
    for f in _collect(args.path, args.since):
        findings += vet_file(f)
    if not findings:
        print(f"{seal('ok')} no insecure patterns found")
        return 0
    role = {"P1": "error", "P2": "muted"}
    for sev in ("P1", "P2"):
        for item in (x for x in findings if x["severity"] == sev):
            print(f"  {paint(f'[{sev}]', role[sev])} {item['message']}")
    p1 = sum(1 for f in findings if f["severity"] == "P1")
    print(f"\n{seal('error' if p1 else 'warn')} {p1} P1 {g('dot')} {len(findings) - p1} P2")
    return 1 if p1 else 0
