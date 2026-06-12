"""inertia-forge — a project-agnostic, deterministic skill-enforcement engine.

The forge makes a skill's methodology *mechanically enforced*: invoking a skill
opens a session with blocking gates; the only way out is to run each phase and
record real, hash-verified evidence. There is no manual close and no escape —
the session auto-closes when the last blocking gate is green.

Quick start (programmatic)::

    from inertia_forge import ForgeSkillBridge
    bridge = ForgeSkillBridge("reviewing_code", "src/")
    bridge.start_session()
    bridge.record_phase("read_changes", Path("src"))
    ...

Evidence modes (per skill, in skill_definitions.yaml):
  - file_analysis  : deterministic code analysis of the target's .py files
  - stamped        : SHA-256 methodology stamp (reasoning skills)
  - enforcer       : pluggable per-skill enforcer (register_enforcer); falls
                     back to stamped if none registered
  - task_management: real task/plan/AC state in the forge's native store
"""
from __future__ import annotations

from inertia_forge.brand import banner, logo, mini_header
from inertia_forge.completion_lock import (
    count_incomplete_blocking_gates,
    get_forge_status,
)
from inertia_forge.palette import paint
from inertia_forge.evidence_collectors import register_enforcer
from inertia_forge.persisted_manifest import PersistedManifest
from inertia_forge.skill_bridge import ForgeSkillBridge
from inertia_forge.skill_registry import (
    get_all_skills,
    get_evidence_mode,
    get_required_steps,
    validate_skill_name,
)

__version__ = "0.24.0"

__all__ = [
    "ForgeSkillBridge",
    "PersistedManifest",
    "count_incomplete_blocking_gates",
    "get_forge_status",
    "register_enforcer",
    "get_all_skills",
    "get_evidence_mode",
    "get_required_steps",
    "validate_skill_name",
    "banner",
    "logo",
    "mini_header",
    "paint",
    "__version__",
]
