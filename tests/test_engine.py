"""Core guarantees of the inertia-forge engine."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from inertia_forge import (
    ForgeSkillBridge,
    count_incomplete_blocking_gates,
    get_evidence_mode,
    get_forge_status,
    get_required_steps,
)
from inertia_forge.completion_lock import _count_gates_for_manifest
from inertia_forge.persisted_manifest import PersistedManifest, _session_filename


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "m.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


class TestLifecycle:
    def test_stamped_skill_auto_closes_when_all_gates_recorded(self, proj: Path) -> None:
        b = ForgeSkillBridge("investigating", "src", claude_session_id="A")
        assert b.start_session()["started"] is True
        assert count_incomplete_blocking_gates("A") == 3
        closed = False
        for ph in get_required_steps("investigating"):
            closed = b.record_phase(ph, Path("src")).get("auto_closed") or closed
        assert closed is True
        assert count_incomplete_blocking_gates("A") == 0
        assert get_forge_status("A") is None

    def test_no_duplicate_session_for_same_target(self, proj: Path) -> None:
        ForgeSkillBridge("investigating", "src", claude_session_id="A").start_session()
        again = ForgeSkillBridge("investigating", "src", claude_session_id="A").start_session()
        assert again["started"] is False


class TestNoEscape:
    def test_p0_phase_keeps_gate_open(self) -> None:
        # A recorded phase that found a P0 does NOT satisfy its gate.
        data = {"skill": "investigating", "phases": {
            "observe": {"evidence_hash": "h", "p0": 0},
            "deduce": {"evidence_hash": "h", "p0": 2},
            "verify": {"evidence_hash": "h", "p0": 0},
        }}
        assert _count_gates_for_manifest(data) == 1

    def test_bypass_marker_keeps_gate_open(self) -> None:
        data = {"skill": "investigating", "phases": {
            "observe": {"evidence_hash": "manual_release_x", "p0": 0},
            "deduce": {"evidence_hash": "h", "p0": 0},
            "verify": {"evidence_hash": "h", "p0": 0},
        }}
        assert _count_gates_for_manifest(data) == 1

    def test_file_analysis_blocks_on_empty_target(self, proj: Path) -> None:
        # implementing_with_tdd is file_analysis; an empty dir yields a P0 that
        # keeps the gate open — you cannot close by pointing at nothing.
        (proj / "empty").mkdir()
        b = ForgeSkillBridge("implementing_with_tdd", "empty", claude_session_id="A")
        b.start_session()
        r = b.record_phase("write_failing_test", proj / "empty")
        assert r["p0"] >= 1
        assert r.get("auto_closed") is not True


class TestOwnerIsolation:
    def test_foreign_session_does_not_trap_this_tab(self, proj: Path) -> None:
        # Tab B's session must not count against tab A's Stop.
        ForgeSkillBridge("investigating", "src", claude_session_id="B").start_session()
        assert count_incomplete_blocking_gates("A") == 0
        assert get_forge_status("A") is None
        assert count_incomplete_blocking_gates("B") == 3

    def test_foreign_session_does_not_suppress_activation(self, proj: Path) -> None:
        ForgeSkillBridge("investigating", "src", claude_session_id="B").start_session()
        # Owner-aware: a different tab's session is not "mine".
        assert PersistedManifest.session_exists(target="src", claude_session_id="A") is False


class TestEvidenceModes:
    def test_modes_resolve(self) -> None:
        assert get_evidence_mode("implementing_with_tdd") == "file_analysis"
        assert get_evidence_mode("reviewing_code") == "stamped"
        assert get_evidence_mode("custom_review") == "enforcer"
        assert get_evidence_mode("pc_plan") == "task_management"

    def test_per_phase_override(self) -> None:
        assert get_evidence_mode("designing_and_implementing", "plan_tasks") == "task_management"
        assert get_evidence_mode("designing_and_implementing", "implement") == "file_analysis"

    def test_enforcer_falls_back_to_stamped_when_unregistered(self, proj: Path) -> None:
        # custom_review is enforcer mode but nothing is registered -> stamped,
        # so its gates are still closeable (clean evidence).
        b = ForgeSkillBridge("custom_review", "src", claude_session_id="A")
        b.start_session()
        closed = False
        for ph in get_required_steps("custom_review"):
            closed = b.record_phase(ph, Path("src")).get("auto_closed") or closed
        assert closed is True


class TestConfigurableSkills:
    def test_env_override(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from inertia_forge import skill_registry as sr
        custom = tmp_path / "my_skills.yaml"
        custom.write_text(
            "my_skill:\n  steps: [a, b]\n  gates: {b: blocking}\n", encoding="utf-8",
        )
        monkeypatch.setenv("INERTIA_FORGE_SKILLS", str(custom))
        sr._cache = None
        try:
            assert sr.validate_skill_name("my_skill") is True
            assert sr.get_required_steps("my_skill") == ["b"]
        finally:
            sr._cache = None
