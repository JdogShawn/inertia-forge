"""Evidence collectors — Bundle E dispatch by skill evidence_mode.

The forge supports three evidence models, selected per-skill in the
YAML registry via ``evidence_mode``:

  file_analysis (default)
      analyze_directory on the target's .py files. Produces P0/P1
      findings from code smells (NotImplementedError, oversized files,
      etc.). Evidence hash = SHA-256 of every .py byte. Used by
      kirby, purge, midas, sharingan — code-producing skills.

  stamped
      Deterministic SHA-256 of {skill|phase|target|timestamp|stamped}.
      No analyzer. Used by reasoning skills whose output is text or
      insight, not code (sherlock, watson). The bridge still applies
      Bundle A protections: unknown phase names yield P0
      'unknown_phase' (synthesized OUTSIDE this collector), and the
      stamp string is non-empty so bypass-prefix rejection passes.

  enforcer
      Dispatch to a per-skill enforcer class in
      inertia_forge.enforcers.* and use its in-memory step tracker.
      Evidence hash is still stamped (the enforcer's contribution is
      tracking, not byte-level evidence). Heals the orphaned Path B
      enforcer subsystem so skills like raphael get first-class
      methodology-aware tracking instead of vacuous file analysis.

All collectors return a uniform (findings, evidence_hash) tuple so
record_phase doesn't care which mode is active.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from inertia_forge.independent_analyzer import (
    analyze_directory,
    compute_evidence_hash,
)


def _stamp_hash(skill: str, phase: str, target: str, marker: str) -> str:
    """Deterministic SHA-256 over the canonical stamp tuple."""
    ts = datetime.now(timezone.utc).isoformat()
    stamp = f"{skill}|{phase}|{target}|{ts}|{marker}"
    return hashlib.sha256(stamp.encode()).hexdigest()


def collect_file_analysis(
    skill: str, phase: str, target: str, analysis_dir: Path,
) -> tuple[list[dict], str]:
    """file_analysis mode — analyze .py files in the target directory."""
    findings = analyze_directory(analysis_dir)
    py_files = (
        sorted(analysis_dir.rglob("*.py"))
        if analysis_dir.exists() else []
    )
    py_files = [f for f in py_files if "__pycache__" not in str(f)]
    return findings, compute_evidence_hash(py_files)


def collect_stamped(
    skill: str, phase: str, target: str, analysis_dir: Path,
) -> tuple[list[dict], str]:
    """stamped mode — reasoning-skill evidence; no analyzer."""
    return [], _stamp_hash(skill, phase, target, "stamped")


def collect_enforcer(
    skill: str, phase: str, target: str, analysis_dir: Path,
) -> tuple[list[dict], str]:
    """enforcer mode — advisory dispatch to per-skill enforcer + stamped evidence.

    HONEST FRAMING (Spotlight audit): this is *advisory dispatch*, not
    full Path B unification. The per-skill enforcer's record_step call
    is a courtesy hook for any in-process auditing the enforcer wants
    to do — but its SkillExecutionTracker state is local to this call
    and garbage-collected when the function returns. **True persistence
    of enforcer state to PersistedManifest is deferred to a future
    bundle.** The evidence hash itself is a deterministic time-stamp,
    same shape as stamped mode.

    If the per-skill enforcer can't be loaded (orphan skill name,
    import error, instantiation failure), fall back to stamped mode so
    the gate still progresses rather than blocking on infrastructure
    issues.
    """
    enforcer_cls = _resolve_enforcer(skill)
    if enforcer_cls is None:
        return collect_stamped(skill, phase, target, analysis_dir)
    try:
        enforcer = enforcer_cls(target)
        # Per-skill enforcers expose record_step / record_state /
        # record_module / record_phase depending on skill — accept
        # any of these via attribute lookup.
        for method_name in (
            "record_step", "record_state", "record_module", "record_phase",
        ):
            if hasattr(enforcer, method_name):
                getattr(enforcer, method_name)(phase, [])
                break
    except Exception:  # noqa: BLE001
        # Broad catch by design (Spotlight item #1): any enforcer
        # failure falls back to pure stamped — the gate's intent is to
        # progress the methodology, not to validate the enforcer's
        # internals. Specific failures should be diagnosed via the
        # enforcer's own tests, not by exploding the bridge.
        pass
    return [], _stamp_hash(skill, phase, target, "enforcer")


# Pluggable enforcer registry (agnostic core). A host project registers a
# per-skill enforcer class via register_enforcer(); the package ships NONE, so
# `enforcer` mode falls back to stamped until one is registered. An enforcer is
# constructed cls(target) and may expose record_step/record_state/
# record_module/record_phase for advisory in-process tracking.
_ENFORCER_REGISTRY: dict[str, type] = {}


def register_enforcer(skill: str, enforcer_cls: type) -> None:
    """Register a per-skill enforcer class for `enforcer` evidence mode."""
    _ENFORCER_REGISTRY[skill.replace("-", "_")] = enforcer_cls


def _resolve_enforcer(skill: str):
    """Return the registered per-skill enforcer class, or None."""
    return _ENFORCER_REGISTRY.get(skill.replace("-", "_"))


def collect_paircoder_mode(
    skill: str, phase: str, target: str, analysis_dir: Path,
) -> tuple[list[dict], str]:
    """task_management mode — verify real bpsai-pair plan/task/AC state.

    Requires the optional [paircoder] extra at runtime (it shells bpsai-pair).
    If the subpackage can't be imported, degrade to stamped so the gate still
    progresses rather than blocking on a missing optional dependency.
    """
    try:
        from inertia_forge.paircoder.evidence import collect_paircoder
    except ImportError:
        import sys
        print(
            "WARNING: evidence_mode 'task_management' needs the optional "
            "[paircoder] extra; falling back to stamped.",
            file=sys.stderr,
        )
        return collect_stamped(skill, phase, target, analysis_dir)
    return collect_paircoder(skill, phase, target, analysis_dir)


_KNOWN_EVIDENCE_MODES = (
    "file_analysis", "stamped", "enforcer", "task_management",
)


def collect(
    skill: str, phase: str, target: str, analysis_dir: Path,
    evidence_mode: str,
) -> tuple[list[dict], str]:
    """Bundle E dispatcher — route to the right collector by mode.

    Unknown evidence_mode falls back to file_analysis (legacy default)
    but emits a stderr WARNING so YAML typos (e.g., "stamp" missing the
    'ed', or "enforce" missing the 'r') don't silently demote a
    reasoning skill to the analyzer path. Spotlight audit item #2.
    """
    if evidence_mode not in _KNOWN_EVIDENCE_MODES:
        import sys
        print(
            f"WARNING: unknown evidence_mode '{evidence_mode}' for skill "
            f"'{skill}' — falling back to file_analysis. Valid modes: "
            f"{', '.join(_KNOWN_EVIDENCE_MODES)}.",
            file=sys.stderr,
        )
    if evidence_mode == "stamped":
        return collect_stamped(skill, phase, target, analysis_dir)
    if evidence_mode == "enforcer":
        return collect_enforcer(skill, phase, target, analysis_dir)
    if evidence_mode == "task_management":
        return collect_paircoder_mode(skill, phase, target, analysis_dir)
    return collect_file_analysis(skill, phase, target, analysis_dir)
