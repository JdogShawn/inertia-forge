"""v0.49.0 — the engage autonomous loop. The whole loop is exercised with ZERO
LLM calls: an injected task_runner (or --dry-run) stands in for the agent.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import tasks
from inertia_forge.cli import main
from inertia_forge.engage import EngageConfig, EngageRunner
from inertia_forge.engage_predispatch import CheckResult, pre_dispatch_check


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


def _task(tid: str, deps: list[str] | None = None, ac: str = "do the work") -> None:
    tasks.add_task(tid, f"task {tid}", 10, [ac], "pytest -q", depends_on=deps or [])


def _cfg(proj: Path, **kw) -> EngageConfig:
    kw.setdefault("commit", False)
    return EngageConfig(project_root=proj, **kw)


class TestRunState:
    def test_roundtrip(self, proj: Path) -> None:
        from inertia_forge.engage_runstate import (
            RunState, load_run_state, save_run_state,
        )
        save_run_state(proj, RunState(run_id="r1", plan_id="p1",
                                      completed_tasks=["T1.1"], paused_task_id="T1.2"))
        loaded = load_run_state(proj, "r1")
        assert loaded.completed_tasks == ["T1.1"] and loaded.paused_task_id == "T1.2"

    def test_traversal_rejected(self, proj: Path) -> None:
        from inertia_forge.engage_runstate import load_run_state, save_run_state, RunState
        with pytest.raises(ValueError):
            save_run_state(proj, RunState(run_id="../evil"))
        with pytest.raises(ValueError):
            load_run_state(proj, "../../etc/passwd")

    def test_pause_state_and_list(self, proj: Path) -> None:
        from inertia_forge.engage_runstate import list_runs, save_pause_state
        rid = save_pause_state(proj, "p1", ["T1.1"], "T1.2")
        assert rid in list_runs(proj)

    def test_missing_raises(self, proj: Path) -> None:
        from inertia_forge.engage_runstate import load_run_state
        with pytest.raises(FileNotFoundError):
            load_run_state(proj, "ghost")


class TestPreDispatch:
    def test_file_exists_satisfied(self, proj: Path) -> None:
        (proj / "mod").mkdir()
        (proj / "mod" / "thing.py").write_text("x = 1", encoding="utf-8")
        assert pre_dispatch_check(["adds `mod/thing.py`"], proj) == CheckResult.ALREADY_SATISFIED

    def test_missing_file_needs_work(self, proj: Path) -> None:
        assert pre_dispatch_check(["adds `mod/ghost.py`"], proj) == CheckResult.NEEDS_WORK

    def test_present_symbol_no_file_is_uncertain(self, proj: Path) -> None:
        # symbol exists in the tree but no file claim → too weak to skip on
        (proj / "lib.py").write_text("def run_thing():\n    pass\n", encoding="utf-8")
        assert pre_dispatch_check(["defines `run_thing`"], proj) == CheckResult.UNCERTAIN

    def test_missing_symbol_needs_work(self, proj: Path) -> None:
        assert pre_dispatch_check(["defines `run_thing`"], proj) == CheckResult.NEEDS_WORK

    def test_no_claims_uncertain(self, proj: Path) -> None:
        assert pre_dispatch_check(["just prose, no code refs"], proj) == CheckResult.UNCERTAIN


class TestSteps:
    def test_build_prompt(self) -> None:
        from inertia_forge.engage_steps import build_task_prompt
        task = {"id": "T1.1", "title": "widget",
                "acceptance_criteria": [{"text": "it works", "done": False}],
                "verification": "pytest -q", "scope": ["src/w.py"]}
        out = build_task_prompt(task)
        assert "T1.1" in out and "it works" in out and "pytest -q" in out and "src/w.py" in out

    def test_mark_done(self, proj: Path) -> None:
        from inertia_forge.engage_steps import mark_task_done
        _task("T1.1")
        mark_task_done("T1.1")
        assert tasks.get_task("T1.1")["status"] == "done"


class TestRunner:
    def test_runs_in_dependency_order(self, proj: Path) -> None:
        _task("T1.1")
        _task("T1.2", deps=["T1.1"])
        seen: list[str] = []
        res = EngageRunner(_cfg(proj), task_runner=lambda t: seen.append(t["id"]) or True).run()
        assert res.completed == ["T1.1", "T1.2"] and seen == ["T1.1", "T1.2"]
        assert res.phases_completed == 2 and not res.failed

    def test_predispatch_skips(self, proj: Path) -> None:
        (proj / "mod").mkdir()
        (proj / "mod" / "done.py").write_text("ok", encoding="utf-8")
        _task("T1.1", ac="adds `mod/done.py`")
        called: list[str] = []
        res = EngageRunner(_cfg(proj), task_runner=lambda t: called.append(t["id"]) or True).run()
        assert "T1.1" in res.skipped and called == []  # never dispatched
        assert tasks.get_task("T1.1")["status"] == "done"

    def test_circuit_breaker_trips(self, proj: Path) -> None:
        _task("T1.1")
        _task("T1.2")  # same wave, both fail → ratio 1.0
        res = EngageRunner(_cfg(proj), task_runner=lambda t: False).run()
        assert res.circuit_breaker_triggered and len(res.failed) == 2
        assert res.failure_reasons["T1.1"] == "agent_failed"

    def test_no_meaningful_output_fails(self, proj: Path, monkeypatch) -> None:
        _task("T1.1")
        import inertia_forge.engage as eng
        monkeypatch.setattr(eng, "commit_task", lambda *a, **k: True)
        monkeypatch.setattr(eng, "verify_output", lambda root: False)
        res = EngageRunner(_cfg(proj, commit=True), task_runner=lambda t: True).run()
        assert res.failed == ["T1.1"] and res.failure_reasons["T1.1"] == "no_meaningful_output"

    def test_human_gate_pauses_and_resumes(self, proj: Path) -> None:
        _task("T1.1")
        data = tasks.load()
        data["tasks"]["T1.1"]["requires"] = "human"
        tasks.save(data)
        res = EngageRunner(_cfg(proj), task_runner=lambda t: True).run()
        assert res.paused_task == "T1.1" and res.run_id
        from inertia_forge.engage_runstate import list_runs
        assert res.run_id in list_runs(proj)
        # human resolves it, resume proceeds (task now done → nothing pending)
        tasks.save({**tasks.load(), "tasks": {**tasks.load()["tasks"]}})
        from inertia_forge.engage_steps import mark_task_done
        mark_task_done("T1.1")
        res2 = EngageRunner(_cfg(proj), task_runner=lambda t: True).run()
        assert res2.paused_task is None and not res2.failed


class TestCli:
    def test_dry_run(self, proj: Path) -> None:
        _task("T1.1")
        assert main(["ignite", "run", "--dry-run"]) == 0
        assert tasks.get_task("T1.1")["status"] == "done"

    def test_runs_empty(self, proj: Path) -> None:
        assert main(["ignite", "runs"]) == 0

    def test_resume_missing_run(self, proj: Path) -> None:
        assert main(["ignite", "resume", "nope"]) == 1
