"""v0.17.0 — backlog validation, plan token estimation, session handoff,
runtime retention/pruning. All deterministic; git stubbed where used.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import backlog, handoff, plan, retention
from inertia_forge import tasks as t
from inertia_forge.cli import main

_GOOD = """# Cart
type: feature

## T1.1: totals
complexity: 5
- [ ] correct
verify: pytest
"""
_BAD = """# Broken
type: maintenance

## T1.1: nothing
"""


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestBacklog:
    def test_good_validates(self) -> None:
        errors, warnings = backlog.validate(_GOOD)
        assert errors == [] and warnings == []

    def test_bad_collects_errors(self) -> None:
        errors, _ = backlog.validate(_BAD)
        joined = " ".join(errors)
        assert "maintenance" in joined and "acceptance criteria" in joined and "verify" in joined

    def test_cli_exit_codes(self, proj, capsys) -> None:
        (proj / "g.md").write_text(_GOOD, encoding="utf-8")
        (proj / "b.md").write_text(_BAD, encoding="utf-8")
        assert main(["backlog", "validate", str(proj / "g.md")]) == 0
        assert main(["backlog", "validate", str(proj / "b.md")]) == 1

    def test_ignite_refuses_invalid(self, proj) -> None:
        (proj / "b.md").write_text(_BAD, encoding="utf-8")
        assert main(["ignite", str(proj / "b.md")]) == 1
        assert t.get_plan() is None  # nothing ingested

    def test_ignite_check_does_not_ingest(self, proj) -> None:
        (proj / "g.md").write_text(_GOOD, encoding="utf-8")
        assert main(["ignite", str(proj / "g.md"), "--check"]) == 0
        assert t.get_plan() is None  # --check validates only


class TestPlanEstimate:
    def test_projects_tokens(self, proj) -> None:
        t.add_task("T1.1", "x", 4, ["a"], "pytest")
        t.add_task("T1.2", "y", 6, ["b"], "pytest")
        est = plan.estimate_plan(tokens_per_point=1000)
        assert est == {"tasks": 2, "points": 10, "tokens": 10000}

    def test_done_tasks_excluded(self, proj) -> None:
        t.add_task("T1.1", "x", 5, ["a"], "pytest")
        t.start_task("T1.1"); t.check_ac("T1.1", 0); t.complete_task("T1.1")
        assert plan.estimate_plan()["tasks"] == 0

    def test_cli_threshold_gate(self, proj) -> None:
        t.add_task("T1.1", "x", 100, ["a"], "pytest")
        assert main(["plan", "estimate", "--threshold", "1000"]) == 1   # over
        assert main(["plan", "estimate", "--threshold", "9999999"]) == 0  # within


class TestHandoff:
    def test_build_includes_ready_and_plan(self, proj, monkeypatch) -> None:
        monkeypatch.setattr("inertia_forge.gitcheck._git", lambda root, *a: "")
        t.create_plan("feature", "demo")
        t.add_task("T1.1", "work", 3, ["a"], "pytest")
        doc = handoff.build()
        assert "Session Handoff" in doc and "demo" in doc and "T1.1" in doc

    def test_write_saves_file(self, proj, monkeypatch) -> None:
        monkeypatch.setattr("inertia_forge.gitcheck._git", lambda root, *a: "")
        assert main(["handoff", "--write"]) == 0
        assert (proj / ".forge" / "handoff.md").exists()

    def test_ascii_clean(self, proj, monkeypatch) -> None:
        monkeypatch.setattr("inertia_forge.gitcheck._git", lambda root, *a: "")
        handoff.build().encode("ascii")  # raises if any non-ASCII slipped in


class TestRetention:
    def test_prune_log_trims(self, proj) -> None:
        retention.LOG.write_text("\n".join(f"e{i}" for i in range(10)) + "\n", encoding="utf-8")
        assert retention.prune_log(keep=4) == 6
        assert retention.LOG.read_text(encoding="utf-8").count("\n") == 4

    def test_prune_log_noop_when_small(self, proj) -> None:
        retention.LOG.write_text("a\nb\n", encoding="utf-8")
        assert retention.prune_log(keep=10) == 0

    def test_prune_cache_by_age(self, proj) -> None:
        retention.CACHE.mkdir()
        blob = retention.CACHE / "old"
        blob.write_text("x", encoding="utf-8")
        future = blob.stat().st_mtime + 40 * 86400
        assert retention.prune_cache(days=30, now=future) == 1
        assert not blob.exists()

    def test_cli(self, proj) -> None:
        assert main(["prune"]) == 0
