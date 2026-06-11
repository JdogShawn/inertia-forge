"""Bypass Prevention — anti-gaming measures from Donatello Passes 1-4.

Covers bypasses #1-#20 and behavioral root causes.
Battle Scars #14 (Self-Grading), #15 (Decorative Enforcement), #16 (Approval Optimization).

Pure deterministic — zero LLM calls.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

# ── Battle Scars ───────────────────────────────────────────────

BATTLE_SCARS: dict[int, dict] = {
    14: {
        "name": "SELF-GRADING (自己採点)",
        "pattern": "AI imports enforcement classes and calls them with fabricated data",
        "detection": "ForgeSessionRequired guard + record_phase computes from findings",
        "sprint": "Sprint 70",
    },
    15: {
        "name": "DECORATIVE ENFORCEMENT (飾り執行)",
        "pattern": "Enforcement code exists but isn't wired into execution path",
        "detection": "ForgeSkillBridge auto-activates forge on every skill invocation",
        "sprint": "Sprint 70",
    },
    16: {
        "name": "APPROVAL OPTIMIZATION (承認最適化)",
        "pattern": "AI optimizes for human approval over correctness",
        "detection": "Mandatory caveats + no-reframing gate + behavioral log",
        "sprint": "Sprint 70",
    },
}


# ── Bypass #1: Protect skill files during forge ────────────────

PROTECTED_DURING_FORGE: list[str] = [
    ".claude/skills/",
    "inertia/forge/",
    "tests/forge/",
]


def is_protected_during_forge(file_path: str) -> bool:
    """Check if a file is protected during an active forge session."""
    normalized = file_path.replace("\\", "/")
    return any(normalized.startswith(p) or p in normalized for p in PROTECTED_DURING_FORGE)


# ── Bypass #4/#15/#20: Analyzer integrity ──────────────────────

ANALYZER_PATH = Path(__file__).parent / "independent_analyzer.py"


def compute_analyzer_checksum() -> str:
    """SHA-256 of the analyzer source — detects modification."""
    if not ANALYZER_PATH.exists():
        return "MISSING"
    return hashlib.sha256(ANALYZER_PATH.read_bytes()).hexdigest()


def verify_analyzer_integrity(expected_checksum: str) -> bool:
    """Verify analyzer hasn't been modified since session start."""
    return compute_analyzer_checksum() == expected_checksum


# ── Bypass #14: No env var backdoors ───────────────────────────

def check_no_env_backdoors(filepath: Path) -> list[dict]:
    """Static analysis: detect os.environ/getenv in analyzer code."""
    findings: list[dict] = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return findings

    for i, line in enumerate(content.splitlines(), 1):
        if re.search(r"os\.environ|os\.getenv|environ\.get", line):
            if not line.strip().startswith("#"):
                findings.append({
                    "severity": "P0",
                    "rule": "env_backdoor",
                    "file": str(filepath),
                    "line": i,
                    "message": f"{filepath.name}:{i}: environment variable access in analyzer (Bypass #14)",
                })
    return findings


# ── Bypass #13: Target scope validation ────────────────────────

def validate_target_scope(target: Path) -> tuple[bool, str]:
    """Target must be a directory with 2+ Python files."""
    if not target.exists():
        return False, f"Target {target} does not exist"
    if not target.is_dir():
        return False, f"Target must be a directory, not a file: {target}"
    py_files = list(target.rglob("*.py"))
    py_files = [f for f in py_files if "__pycache__" not in str(f)]
    if len(py_files) < 2:
        return False, f"Target has {len(py_files)} Python files — need 2+ for meaningful analysis"
    return True, f"{len(py_files)} Python files found"


# ── Bypass #17: Session-specific salt ──────────────────────────

def generate_session_salt() -> str:
    """Random salt for manifest integrity — prevents hash precomputation."""
    import uuid
    return str(uuid.uuid4())


# ── Behavioral: Persistent behavioral log ──────────────────────

BEHAVIORAL_LOG_PATH = Path(".forge/behavioral_log.jsonl")


def log_behavioral_event(event_type: str, details: str) -> None:
    """Append-only behavioral log — survives across sessions."""
    BEHAVIORAL_LOG_PATH.parent.mkdir(exist_ok=True)
    entry = {
        "type": event_type,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(BEHAVIORAL_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def read_behavioral_log(max_entries: int = 50) -> list[dict]:
    """Read past behavioral events."""
    if not BEHAVIORAL_LOG_PATH.exists():
        return []
    entries: list[dict] = []
    with open(BEHAVIORAL_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries[-max_entries:]


# ── Behavioral: Claim verification ─────────────────────────────

CLAIMS_LOG_PATH = Path(".forge/claims.jsonl")


def log_claim(claim: str, source: str = "claude") -> None:
    """Log a claim made during skill execution."""
    CLAIMS_LOG_PATH.parent.mkdir(exist_ok=True)
    entry = {
        "claim": claim,
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verified": False,
    }
    with open(CLAIMS_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def verify_claims_against_manifest(manifest_data: dict) -> list[dict]:
    """Compare logged claims against actual manifest findings."""
    if not CLAIMS_LOG_PATH.exists():
        return []
    mismatches: list[dict] = []
    claims = []
    with open(CLAIMS_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    claims.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    phases = manifest_data.get("phases", {})
    total_p0 = sum(p.get("p0", 0) for p in phases.values())
    total_p1 = sum(p.get("p1", 0) for p in phases.values())

    for claim in claims:
        text = claim.get("claim", "").lower()
        if "zero debt" in text and (total_p0 > 0 or total_p1 > 0):
            mismatches.append({
                "claim": claim["claim"],
                "reality": f"Manifest shows P0={total_p0}, P1={total_p1}",
                "verdict": "MISMATCH",
            })
        if "diamond" in text and total_p0 > 0:
            mismatches.append({
                "claim": claim["claim"],
                "reality": f"Manifest has {total_p0} P0 findings — not Diamond",
                "verdict": "MISMATCH",
            })

    return mismatches


# ── Scope warning ──────────────────────────────────────────────

def check_sprint_scope(task_count: int, threshold: int = 50) -> str | None:
    """Warn if sprint has too many tasks."""
    if task_count > threshold:
        return (f"WARNING: Sprint has {task_count} tasks. "
                f"Typical INERTIA sprint is 30-40. Confirm scope.")
    return None


# ── Mandatory caveats ──────────────────────────────────────────

REQUIRED_CAVEATS = [
    "What was NOT checked",
    "What could be wrong",
    "What human should verify",
]


def check_caveats_present(output: str) -> list[str]:
    """Verify mandatory caveats are present in skill output."""
    missing = []
    lower = output.lower()
    for caveat in REQUIRED_CAVEATS:
        if caveat.lower() not in lower:
            missing.append(caveat)
    return missing
