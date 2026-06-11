"""Native (dependency-free) task management + task_management evidence mode."""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import ForgeSkillBridge, get_required_steps, tasks as t
from inertia_forge.task_evidence import collect_native_task


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


def _p0(phase: str) -> set[str]:
    findings, _ = collect_native_task("pc_plan", phase, ".", Path("."))
    return {f["rule"] for f in findings}


class TestStore:
    def test_create_plan_rejects_bad_type(self, proj: Path) -> None:
        with pytest.raises(ValueError):
            t.create_plan("maintenance", "x")
        assert t.create_plan("feature", "x")["type"] == "feature"

    def test_add_task_validates(self, proj: Path) -> None:
        with pytest.raises(ValueError):  # bad id
            t.add_task("TASK-9", "x", 5, ["a"], "pytest")
        with pytest.raises(ValueError):  # no AC
            t.add_task("T1.1", "x", 5, [], "pytest")
        with pytest.raises(ValueError):  # no verification
            t.add_task("T1.2", "x", 5, ["a"], "")
        assert t.add_task("T1.1", "x", 5, ["a"], "pytest")["status"] == "pending"

    def test_complete_requires_all_ac(self, proj: Path) -> None:
        t.add_task("T1.1", "x", 5, ["a", "b"], "pytest")
        t.start_task("T1.1")
        with pytest.raises(ValueError):
            t.complete_task("T1.1")
        t.check_ac("T1.1", 0)
        t.check_ac("T1.1", 1)
        assert t.complete_task("T1.1")["status"] == "done"

    def test_persists_to_forge_dir(self, proj: Path) -> None:
        t.add_task("T1.1", "x", 5, ["a"], "pytest")
        assert (proj / ".forge" / "forge_tasks.json").exists()


class TestVerifiers:
    def test_budget_and_plan_and_tasks(self, proj: Path) -> None:
        assert "no_plan" in _p0("create_plan")
        assert "no_tasks" in _p0("add_tasks")
        assert "budget_not_estimated" in _p0("budget_check")
        t.create_plan("bugfix", "x")
        t.add_task("T1.1", "x", 5, ["a"], "pytest")
        assert _p0("create_plan") == set()
        assert _p0("add_tasks") == set()
        assert _p0("budget_check") == set()

    def test_complexity_out_of_range(self, proj: Path) -> None:
        t.add_task("T1.1", "x", 5, ["a"], "pytest")
        # hand-tamper the store to an out-of-range value
        data = t.load(); data["tasks"]["T1.1"]["complexity"] = 200; t.save(data)
        assert "complexity_out_of_range" in _p0("budget_check")

    def test_preflight_and_complete(self, proj: Path) -> None:
        assert "no_active_task" in _p0("preflight")
        t.add_task("T1.1", "x", 5, ["a"], "pytest")
        t.start_task("T1.1")
        assert _p0("preflight") == set()
        assert "ac_unmet" in _p0("complete")
        t.check_ac("T1.1", 0)
        t.complete_task("T1.1")
        assert _p0("complete") == set()


class TestEndToEnd:
    def test_start_task_session_gates_on_native_store(self, proj: Path) -> None:
        # start_task is task_management; preflight blocks until a task is started.
        b = ForgeSkillBridge("start_task", ".", claude_session_id="A")
        b.start_session()
        r = b.record_phase("preflight", Path("."))
        assert r["p0"] >= 1                    # no active task yet -> gate stays red

        t.add_task("T1.1", "do it", 5, ["works"], "pytest")
        t.start_task("T1.1")
        assert b.record_phase("preflight", Path("."))["p0"] == 0

        t.check_ac("T1.1", 0)
        t.complete_task("T1.1")
        closed = b.record_phase("complete", Path(".")).get("auto_closed")
        assert closed is True                  # both gates green -> auto-close
