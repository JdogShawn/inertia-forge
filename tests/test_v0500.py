"""v0.50.0 — ignite depth: targeted tests, recovery guidance, review-and-fix
loop. All exercised with zero LLM calls (injected runners / review fns).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import tasks
from inertia_forge.ignite_engine import IgniteConfig, IgniteRunner
from inertia_forge.ignite_recovery import recovery_guidance
from inertia_forge.ignite_review import ReviewOutcome
from inertia_forge.ignite_targeted import build_test_instruction, map_source_to_test


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


def _task(tid: str, deps: list[str] | None = None) -> None:
    tasks.add_task(tid, f"task {tid}", 10, ["do the work"], "pytest -q", depends_on=deps or [])


def _cfg(proj: Path, **kw) -> IgniteConfig:
    kw.setdefault("commit", False)
    kw.setdefault("targeted_tests", False)
    return IgniteConfig(project_root=proj, **kw)


class TestTargeted:
    def test_map_src_layout(self) -> None:
        assert map_source_to_test("src/inertia_forge/ignite.py") == "tests/test_ignite.py"

    def test_map_nested(self) -> None:
        assert map_source_to_test("pkg/sub/mod.py") == "tests/sub/test_mod.py"

    def test_skips_init_and_tests(self) -> None:
        assert map_source_to_test("src/pkg/__init__.py") is None
        assert map_source_to_test("tests/test_x.py") is None
        assert map_source_to_test("../evil.py") is None

    def test_instruction(self) -> None:
        assert build_test_instruction([]) == ""
        assert "pytest tests/test_a.py" in build_test_instruction(["tests/test_a.py"])


class TestRecovery:
    def test_dominant_cause(self) -> None:
        lines = recovery_guidance({"T1.1": "no_meaningful_output", "T1.2": "no_meaningful_output",
                                   "T1.3": "agent_failed"})
        assert "no meaningful output" in lines[0] and "resume" in lines[1]

    def test_empty(self) -> None:
        assert len(recovery_guidance({})) == 1



class TestReviewWiring:
    def test_unresolved_review_fails_task(self, proj: Path) -> None:
        _task("T1.1")
        runner = IgniteRunner(
            _cfg(proj), task_runner=lambda t: True,
            review_fn=lambda t: ReviewOutcome(resolved=False, iterations=3, findings="x"))
        res = runner.run()
        assert res.failed == ["T1.1"] and res.failure_reasons["T1.1"] == "review_unresolved"
        assert "T1.1" not in res.completed

    def test_resolved_review_passes(self, proj: Path) -> None:
        _task("T1.1")
        runner = IgniteRunner(
            _cfg(proj), task_runner=lambda t: True,
            review_fn=lambda t: ReviewOutcome(resolved=True, iterations=1))
        res = runner.run()
        assert res.completed == ["T1.1"] and not res.failed


class TestReviewLoop:
    """ignite_review now delegates the review judgment to review_agents.review_diff
    (diff-based, P0/P1/P2). This module owns only the fix loop."""

    def test_clean_first_pass(self, proj: Path, monkeypatch) -> None:
        import inertia_forge.ignite_review as r
        from inertia_forge.review_agents import ReviewResult
        monkeypatch.setattr("inertia_forge.review_agents.review_diff",
                            lambda *a, **k: ReviewResult(action="approve"))
        out = r.review_and_fix({"id": "T1.1", "title": "t"}, _cfg(proj), max_iterations=3)
        assert out.resolved and out.iterations == 1

    def test_blocking_exhausts(self, proj: Path, monkeypatch) -> None:
        import inertia_forge.ignite_review as r
        from inertia_forge.review_agents import ReviewResult
        monkeypatch.setattr("inertia_forge.review_agents.review_diff",
                            lambda *a, **k: ReviewResult(
                                action="request_changes", findings=[("caliper", "### P0 bad")]))

        class _Sess:  # the fixer — no-op
            def __init__(self, *a, **k): ...
            def invoke(self, prompt): return type("R", (), {"is_error": False, "result": ""})()
        monkeypatch.setattr("inertia_forge.agent.AgentSession", _Sess)
        out = r.review_and_fix({"id": "T1.1", "title": "t"}, _cfg(proj), max_iterations=2)
        assert not out.resolved and out.iterations == 2
