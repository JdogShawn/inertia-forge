"""v0.53.0 — agent-backed review intelligence (review_agents). The deterministic
scaffolding (severity classification, size heuristic, dispatch loop) is tested
with an injected dispatcher; no test invokes a real agent.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import review_agents as ra
from inertia_forge.cli import main


class TestClassification:
    def test_blocking(self) -> None:
        assert ra.has_blocking_findings("### P0 crash") is True
        assert ra.has_blocking_findings("### P1 important") is True
        assert ra.has_blocking_findings("### P2 minor") is False

    def test_action(self) -> None:
        assert ra.classify_review_action("### P0 x") == "request_changes"
        assert ra.classify_review_action("### P2 x") == "comment"
        assert ra.classify_review_action("looks great") == "approve"


class TestSizeHeuristic:
    _BIG = "diff --git a/x b/x\n" + "\n".join("+l%d" % i for i in range(600))

    def test_diff_size(self) -> None:
        lines, files = ra.diff_size("diff --git a/x b/x\n+added\n-removed\n")
        assert lines == 2 and files == 1

    def test_cross_cutting_on_large(self) -> None:
        assert ra.reviewers_for_diff("diff --git a/x b/x\n+one\n") == ["caliper", "sentinel"]
        assert "lattice" in ra.reviewers_for_diff(self._BIG)


class TestReviewDiff:
    def test_empty_diff_approves(self) -> None:
        assert ra.review_diff("   ").action == "approve"

    def test_request_changes_on_p0(self) -> None:
        res = ra.review_diff("diff --git a/x b/x\n+bug\n", agents=["caliper"],
                             dispatcher=lambda n, p: "### P0 null deref")
        assert res.action == "request_changes" and res.findings[0][0] == "caliper"

    def test_data_fence_wraps_diff(self) -> None:
        seen = {}
        ra.review_diff("diff --git a/x b/x\n+secret\n", agents=["sentinel"],
                       dispatcher=lambda n, p: seen.setdefault("p", p) or "### P2 ok")
        assert "DATA START" in seen["p"] and "DATA END" in seen["p"] and "+secret" in seen["p"]

    def test_all_agents_fail_is_error(self) -> None:
        res = ra.review_diff("diff --git a/x b/x\n+x\n", agents=["caliper", "sentinel"],
                             dispatcher=lambda n, p: None)
        assert res.action == "error" and res.errors == 2 and not res.findings

    def test_multi_agent_combines(self) -> None:
        res = ra.review_diff("diff --git a/x b/x\n+x\n", agents=["caliper", "sentinel"],
                             dispatcher=lambda n, p: "### P2 minor")
        assert res.action == "comment" and len(res.findings) == 2


class TestCli:
    def test_cli_diff_approve(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        # no git repo → empty diff → approve, exit 0
        assert main(["review-agent", "diff"]) == 0

    def test_cli_request_changes_exit1(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(ra, "_diff_for", lambda *a, **k: "diff --git a/x b/x\n+bug\n")
        monkeypatch.setattr(ra, "review_diff",
                            lambda *a, **k: ra.ReviewResult(action="request_changes",
                                                            findings=[("caliper", "### P0 bad")]))
        assert main(["review-agent", "diff"]) == 1
