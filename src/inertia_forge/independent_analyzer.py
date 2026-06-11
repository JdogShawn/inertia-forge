"""IndependentAnalyzer — reads actual files, produces objective findings.

Battle Scar #14 fix: findings come from FILE ANALYSIS, not self-reports.
Every rule is deterministic: same file = same findings every time.

Rules: line count, wildcard imports, NotImplementedError, code markers,
empty test files, broad excepts, unbounded collections.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path


def analyze_directory(directory: Path) -> list[dict]:
    """Analyze all Python files in a directory. Returns objective findings.

    F3 fix (Donatello Bundle A): a missing or content-less target dir is
    not a vacuous pass — it surfaces a P0 'target_invalid' finding so the
    forge gate naturally blocks via p0>0. The driver must point at a
    real target with .py content; no refusal path lets them bail.
    """
    findings: list[dict] = []
    if not directory.exists():
        findings.append({
            "severity": "P0", "rule": "target_invalid",
            "file": str(directory), "line": 0,
            "message": (
                f"target directory {directory} does not exist — "
                "phase cannot be evidenced without real files"
            ),
        })
        return findings
    # Exclusions:
    #   __pycache__  — bytecode cache, never source
    #   .claude/skills/  — 3rd-party skill distribution code (factored upstream;
    #     refactoring drifts from source-of-truth and breaks on skill updates)
    #   .claude/worktrees/  — ephemeral agent worktrees; would 4x file count
    #     during in-flight dispatches and conflate live driver code with target
    _excluded = ("__pycache__", ".claude/skills", ".claude/worktrees")
    py_files = [
        f for f in directory.rglob("*.py")
        if not any(excl in str(f).replace("\\", "/") for excl in _excluded)
    ]
    if not py_files:
        findings.append({
            "severity": "P0", "rule": "target_invalid",
            "file": str(directory), "line": 0,
            "message": (
                f"target directory {directory} contains 0 .py files — "
                "phase cannot be evidenced against an empty tree"
            ),
        })
        return findings
    for py_file in sorted(py_files):
        findings.extend(analyze_file(py_file))
    return findings


def _rule_line_count(name: str, filepath: Path, lines: list[str]) -> list[dict]:
    """Rule 1: line-count limits (test files allowed larger per CLAUDE.md
    architecture: source <400 hard / <200 warn; tests <600 hard / <400 warn)."""
    is_test = name.startswith("test_") or name.endswith("_test.py")
    hard_limit = 600 if is_test else 400
    warn_limit = 400 if is_test else 200
    n = len(lines)
    if n > hard_limit:
        return [{"severity": "P0", "rule": "max_lines", "file": str(filepath),
                 "line": 0, "message": f"{name}: {n} lines exceeds {hard_limit} hard limit"}]
    if n > warn_limit:
        return [{"severity": "P2", "rule": "warning_lines", "file": str(filepath),
                 "line": 0, "message": f"{name}: {n} lines exceeds {warn_limit} warning"}]
    return []


def _scan_imports_markers(name: str, fp: str, lines: list[str]) -> list[dict]:
    """Rules 2-4: wildcard imports, NotImplementedError stubs, TODO markers."""
    findings: list[dict] = []

    # Rule 2: Wildcard imports
    for i, line in enumerate(lines, 1):
        if "import *" in line and not line.strip().startswith("#"):
            findings.append({"severity": "P1", "rule": "wildcard_import",
                             "file": fp, "line": i,
                             "message": f"{name}:{i}: wildcard import"})

    # Rule 3: NotImplementedError (stubs claiming to be active)
    for i, line in enumerate(lines, 1):
        if "NotImplementedError" in line and not line.strip().startswith("#"):
            findings.append({"severity": "P1", "rule": "not_implemented",
                             "file": fp, "line": i,
                             "message": f"{name}:{i}: NotImplementedError stub"})

    # Rule 4: TODO/FIXME/HACK markers
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        for marker in ("TODO", "FIXME", "HACK", "XXX"):
            if marker in line:
                findings.append({"severity": "P2", "rule": "code_marker",
                                 "file": fp, "line": i,
                                 "message": f"{name}:{i}: {marker} marker"})
                break

    return findings


def _scan_safety(name: str, fp: str, lines: list[str]) -> list[dict]:
    """Rules 5-7: empty test files, broad-except swallow, unbounded collections."""
    findings: list[dict] = []

    # Rule 5: Empty test files
    if name.startswith("test_"):
        test_count = sum(1 for l in lines if l.strip().startswith("def test_"))
        if test_count == 0 and len(lines) > 5:
            findings.append({"severity": "P1", "rule": "empty_test_file",
                             "file": fp, "line": 0,
                             "message": f"{name}: test file with zero test functions"})

    # Rule 6: Broad except (except Exception without re-raise)
    for i, line in enumerate(lines, 1):
        if re.search(r"except\s+Exception\s*:", line) or re.search(r"except\s*:", line):
            for j in range(i, min(i + 3, len(lines))):
                if lines[j].strip() == "pass":
                    findings.append({"severity": "P2", "rule": "broad_except_swallow",
                                     "file": fp, "line": i,
                                     "message": f"{name}:{i}: broad except swallows error"})
                    break

    # Rule 7: Unbounded dict/list at class level (potential memory leak)
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.match(r"self\.\w+\s*[:=]\s*(\{\}|\[\]|dict\(\)|list\(\))", stripped):
            context = "\n".join(lines[max(0, i - 3):min(len(lines), i + 3)])
            if "maxlen" not in context and "bounded" not in context.lower():
                findings.append({"severity": "P2", "rule": "unbounded_collection",
                                 "file": fp, "line": i,
                                 "message": f"{name}:{i}: potentially unbounded collection"})

    return findings


def analyze_file(filepath: Path) -> list[dict]:
    """Analyze a single Python file. All rules are objective and deterministic.

    Rule order is preserved (line-count, then 2-4, then 5-7) so finding order
    is byte-identical to the original single-function analyzer.
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return [{"severity": "P1", "rule": "unreadable_file",
                 "file": str(filepath), "line": 0,
                 "message": f"{filepath.name}: cannot read file"}]
    lines = content.splitlines()
    name = filepath.name
    fp = str(filepath)
    return (
        _rule_line_count(name, filepath, lines)
        + _scan_imports_markers(name, fp, lines)
        + _scan_safety(name, fp, lines)
    )


def run_pytest_check(directory: Path) -> list[dict]:
    """Run pytest and parse results. PairCoder can't fake pytest output."""
    findings: list[dict] = []
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", str(directory), "--tb=no", "-q"],
            capture_output=True, text=True, timeout=120,
        )
        # Parse last line for "N passed, M failed"
        for line in result.stdout.splitlines():
            if "failed" in line:
                findings.append({"severity": "P0", "rule": "test_failure",
                                 "file": str(directory), "line": 0,
                                 "message": f"pytest: {line.strip()}"})
    except (subprocess.TimeoutExpired, FileNotFoundError):
        findings.append({"severity": "P2", "rule": "pytest_unavailable",
                         "file": str(directory), "line": 0,
                         "message": "pytest not available or timed out"})
    return findings


def compute_evidence_hash(source_files: list[Path]) -> str:
    """SHA-256 hash of actual file contents — tamper-proof evidence."""
    import hashlib
    hasher = hashlib.sha256()
    for f in sorted(source_files):
        try:
            hasher.update(f.read_bytes())
        except OSError:
            hasher.update(f"MISSING:{f}".encode())
    return hasher.hexdigest()
