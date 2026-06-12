"""v0.54.0 — the ignite pipeline: security gate, finalize, planning, run.

Behaviors cross-referenced from the ignite source: the gate fail-closes (agent
error blocks), a P0 blocks, a security block halts finalize before review, and
the plan parser extracts the structured sections. All zero-LLM via injected
dispatchers / monkeypatched diffs.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import ignite_finalize as ifin
from inertia_forge import ignite_security as isec
from inertia_forge.ignite_engine import IgniteResult


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


_DIFF = "diff --git a/x b/x\n+secret = 1\n"


class TestSecurityGate:
    def test_no_diff_skips(self, proj: Path) -> None:
        # no git repo → empty diff → gate skipped, not blocked
        assert isec.security_gate(proj)["action"] == "skipped"

    def test_p0_blocks(self, proj: Path, monkeypatch) -> None:
        monkeypatch.setattr(isec, "branch_diff", lambda *a, **k: _DIFF)
        res = isec.security_gate(proj, dispatcher=lambda ctx: "### P0 hardcoded secret")
        assert res["blocked"] and res["action"] == "request_changes"

    def test_agent_error_fail_closed(self, proj: Path, monkeypatch) -> None:
        monkeypatch.setattr(isec, "branch_diff", lambda *a, **k: _DIFF)
        res = isec.security_gate(proj, dispatcher=lambda ctx: None)  # agent error
        assert res["blocked"] and res["action"] == "error"

    def test_clean_approves(self, proj: Path, monkeypatch) -> None:
        monkeypatch.setattr(isec, "branch_diff", lambda *a, **k: _DIFF)
        res = isec.security_gate(proj, dispatcher=lambda ctx: "### P2 nit only")
        assert not res["blocked"] and res["action"] == "approve"


class TestFinalize:
    def _result(self) -> IgniteResult:
        return IgniteResult(completed=["T1.1"], phases_completed=1)

    def test_security_block_halts(self, proj: Path, monkeypatch) -> None:
        monkeypatch.setattr(isec, "branch_diff", lambda *a, **k: _DIFF)
        out = ifin.finalize(self._result(), proj,
                            sec_dispatcher=lambda ctx: "### P0 bad",
                            review_dispatcher=lambda n, c: "### P2 should-not-run")
        assert out["security_blocked"] and out["review"] is None

    def test_clean_runs_review(self, proj: Path, monkeypatch) -> None:
        monkeypatch.setattr(isec, "branch_diff", lambda *a, **k: _DIFF)
        out = ifin.finalize(self._result(), proj,
                            sec_dispatcher=lambda ctx: "looks clean",
                            review_dispatcher=lambda n, c: "### P1 fix this")
        assert not out["security_blocked"]
        assert out["review"]["action"] == "request_changes"


class TestPlanParse:
    def test_sections(self) -> None:
        from inertia_forge.ignite_plan import parse_plan
        md = ("## Summary\nBuild the widget.\n\n"
              "## Phases\n### Phase 1: setup\n- scaffold\n- config\n\n"
              "## Files to Modify\n- src/w.py\n\n"
              "## Complexity\nhigh\n\n## Risks\n- flaky tests")
        out = parse_plan(md)
        assert out.summary == "Build the widget." and out.complexity == "high"
        assert out.phases[0].name == "setup" and "scaffold" in out.phases[0].tasks
        assert out.files == ["src/w.py"] and out.risks == ["flaky tests"]

    def test_plan_goal_dispatcher(self, proj: Path) -> None:
        from inertia_forge.ignite_plan import plan_goal
        out = plan_goal("a goal", dispatcher=lambda p: "## Summary\ndone\n## Complexity\nlow")
        assert out.summary == "done" and out.complexity == "low"

    def test_plan_goal_agent_error_returns_none(self, proj: Path) -> None:
        from inertia_forge.ignite_plan import plan_goal
        assert plan_goal("g", dispatcher=lambda p: None) is None


class TestRunPipelineCli:
    def test_dry_run_no_finalize(self, proj: Path) -> None:
        from inertia_forge import tasks
        from inertia_forge.cli import main
        tasks.add_task("T1.1", "t", 5, ["works"], "pytest -q")
        # dry-run executes with zero LLM and never reaches finalize
        assert main(["ignite", "run", "--dry-run"]) == 0
        assert tasks.get_task("T1.1")["status"] == "done"
