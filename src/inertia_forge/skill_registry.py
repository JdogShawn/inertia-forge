"""縛り Skill Step Registry — YAML-driven skill definitions with quality gates.

Loads skill definitions from skill_definitions.yaml. Each skill declares
ordered steps, gate types (blocking/checkpoint/advisory), and loop limits.
No hardcoded Python — all data lives in YAML.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# ── Data Model ───────────────────────────────────────────────

_MAX_SKILLS = 50


@dataclass(frozen=True)
class SkillDefinition:
    """Immutable definition of a skill's phases, gates, and loop limit.

    target_override (Bundle C F8): when non-empty, auto-fire hooks route
    this skill's forge session at the override path instead of the
    default backend/. Lives in the YAML registry so adding a new
    cross-repo skill doesn't require editing both shell hooks.

    evidence_mode (Bundle E F10): which evidence-recording path the
    bridge uses for record_phase. Three modes:
      - "file_analysis" (default): analyze_directory on target's .py
        files — for code-producing skills (kirby, purge, midas, etc.).
      - "stamped": SHA-256 of {skill|phase|target|timestamp} — for
        reasoning skills whose output is text, not code (sherlock,
        watson, donatello, raphael — anything that produces insight
        rather than file changes). Bypass-prevention still applies:
        bypass-prefix evidence rejected, unknown phase names yield P0.
      - "enforcer": dispatch to a per-skill enforcer class in
        inertia_forge.enforcers.* (Path B). Heals the orphaned
        per-skill enforcer subsystem so caller-provided findings
        become first-class evidence for skills like raphael.
    """

    name: str
    steps: tuple[str, ...]
    gates: dict[str, str]
    # Advisory only: the intended max methodology iterations. The forge's gate
    # model is record-until-green (not iteration-bounded), so loop_max is not a
    # hard gate — it documents intent and is surfaced by `skills validate`.
    loop_max: int
    target_override: str = ""
    evidence_mode: str = "file_analysis"
    # Per-phase evidence_mode overrides (Bundle G). Lets one skill gate
    # planning phases on task-state while its code phases stay on arch —
    # e.g. designing-and-implementing: {plan_tasks: task_management}.
    phase_evidence: dict[str, str] = field(default_factory=dict)
    # Optional methodology-doc path; enforced by `doc_reading` evidence mode
    # (a phase stays red until `inertia-forge read <skill>` marks it read).
    doc: str = ""


# ── Module-level cache ───────────────────────────────────────

import os

_PACKAGED_YAML = Path(__file__).parent / "skill_definitions.yaml"
_cache: dict[str, SkillDefinition] | None = None


def resolve_yaml_path() -> Path:
    """Locate the active skill_definitions YAML (first hit wins):

    1. $INERTIA_FORGE_SKILLS         — explicit override
    2. ./forge_skills.yaml           — project-local
    3. ./.forge/skills.yaml          — project-local (hidden)
    4. packaged generic starter      — ships with inertia-forge
    """
    env = os.environ.get("INERTIA_FORGE_SKILLS")
    if env and Path(env).is_file():
        return Path(env)
    for candidate in (Path("forge_skills.yaml"), Path(".forge") / "skills.yaml"):
        if candidate.is_file():
            return candidate
    return _PACKAGED_YAML


def _load_registry() -> dict[str, SkillDefinition]:
    """Parse YAML and build the skill registry. Cached on first call."""
    global _cache
    if _cache is not None:
        return _cache

    with open(resolve_yaml_path(), encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f)

    registry: dict[str, SkillDefinition] = {}
    for name, data in raw.items():
        if len(registry) >= _MAX_SKILLS:
            break
        registry[name] = SkillDefinition(
            name=name,
            steps=tuple(data["steps"]),
            gates=dict(data.get("gates", {})),
            loop_max=int(data.get("loop_max", 0)),
            target_override=str(data.get("target_override", "")),
            evidence_mode=str(data.get("evidence_mode", "file_analysis")),
            phase_evidence=dict(data.get("phase_evidence", {})),
            doc=str(data.get("doc", "")),
        )

    _cache = registry
    return _cache


# ── Public API ───────────────────────────────────────────────


def _normalize(name: str) -> str:
    """Normalize skill name for registry lookup.

    Skill files use kebab-case (dispatching-kirby-waves) but YAML registry
    keys are snake_case (dispatching_kirby_waves). All public functions
    normalize input so callers don't have to care which form they pass.
    """
    return name.replace("-", "_") if name else name


def get_skill(name: str) -> SkillDefinition:
    """Return a single skill definition. Raises ValueError if not found."""
    registry = _load_registry()
    normalized = _normalize(name)
    if normalized not in registry:
        raise ValueError(f"Unknown skill: {name!r}")
    return registry[normalized]


def get_all_skills() -> dict[str, SkillDefinition]:
    """Return all registered skill definitions."""
    return dict(_load_registry())


def get_required_steps(name: str) -> list[str]:
    """Return only the steps with a 'blocking' gate for a skill."""
    skill = get_skill(name)
    return [s for s in skill.steps if skill.gates.get(s) == "blocking"]


def validate_skill_name(name: str) -> bool:
    """Check whether a skill name exists in the registry.

    Accepts both kebab-case (dispatching-kirby-waves) and snake_case
    (dispatching_kirby_waves) — internally normalized to snake.
    """
    if not name:
        return False
    registry = _load_registry()
    return _normalize(name) in registry


def get_target_override(name: str) -> str:
    """Bundle C (F8): return the per-skill target override or empty.

    Replaces hardcoded case statements in the auto-fire shell hooks.
    Hooks call this and use the empty fallback to mean "no override —
    use the default backend/ target or the active task's scope[0]".
    """
    if not name:
        return ""
    registry = _load_registry()
    skill = registry.get(_normalize(name))
    if skill is None:
        return ""
    return skill.target_override


def get_evidence_mode(name: str, phase: str | None = None) -> str:
    """Bundle E/G: return the evidence_mode for a skill (and optional phase).

    Resolution order:
      1. per-phase override (skill.phase_evidence[phase]) — Bundle G
      2. per-skill evidence_mode
      3. "file_analysis" (fail-open to legacy behavior)

    Used by ForgeSkillBridge.record_phase to dispatch between
    file_analysis / stamped / enforcer / task_management.
    """
    if not name:
        return "file_analysis"
    registry = _load_registry()
    skill = registry.get(_normalize(name))
    if skill is None:
        return "file_analysis"
    if phase and skill.phase_evidence.get(phase):
        return skill.phase_evidence[phase]
    return skill.evidence_mode or "file_analysis"
