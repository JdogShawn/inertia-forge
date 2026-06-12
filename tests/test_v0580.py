"""v0.58.0 — PR finalize polish: base auto-detect, skip-if-exists, blocked in body."""
from pathlib import Path
import pytest
from inertia_forge import ignite_finalize as ifin
from inertia_forge.ignite_engine import IgniteResult


def test_pr_body_includes_blocked():
    r = IgniteResult(completed=["T1.1"], failed=["T1.2"], blocked=["T1.3"],
                     failure_reasons={"T1.2": "agent_failed", "T1.3": "dependency_blocked"})
    body = ifin._pr_body(r)
    assert "## Completed" in body and "## Failed" in body and "## Blocked" in body
    assert "dependency_blocked" in body


def test_detect_base_prefers_dev(monkeypatch):
    monkeypatch.setattr("inertia_forge.gitcheck._git", lambda root, *a: "main\ndev\nfeature/x")
    assert ifin._detect_base(Path("."), "main") == "main"   # preferred exists
    monkeypatch.setattr("inertia_forge.gitcheck._git", lambda root, *a: "dev\nfeature/x")
    assert ifin._detect_base(Path("."), "nope") == "dev"    # preferred absent → dev
    monkeypatch.setattr("inertia_forge.gitcheck._git", lambda root, *a: "feature/x")
    assert ifin._detect_base(Path("."), "nope") == "main"   # no dev → main


class TestBacklogDepValidation:
    def test_cycle_rejected(self):
        from inertia_forge.backlog import validate
        errs, _ = validate("## T1.1: a\ndepends_on: T1.2\nverify: pytest\n- [ ] x\n\n"
                           "## T1.2: b\ndepends_on: T1.1\nverify: pytest\n- [ ] y\n")
        assert any("cycle" in e for e in errs)

    def test_unknown_dep_rejected(self):
        from inertia_forge.backlog import validate
        errs, _ = validate("## T1.1: a\ndepends_on: T9.9\nverify: pytest\n- [ ] x\n")
        assert any("unknown task" in e for e in errs)

    def test_clean_deps_ok(self):
        from inertia_forge.backlog import validate
        errs, _ = validate("## T1.1: a\nverify: pytest\n- [ ] x\n\n"
                           "## T1.2: b\ndepends_on: T1.1\nverify: pytest\n- [ ] y\n")
        assert not errs


class TestModelRouting:
    def test_routes_by_complexity(self):
        from inertia_forge.ignite_steps import resolve_model
        cfg = type("C", (), {"model": "default", "model_routing": {
            "small": {"max": 20, "model": "haiku"}, "mid": {"max": 60, "model": "sonnet"},
            "big": {"max": 100, "model": "opus"}}})()
        assert resolve_model({"complexity": 10}, cfg) == "haiku"
        assert resolve_model({"complexity": 45}, cfg) == "sonnet"
        assert resolve_model({"complexity": 90}, cfg) == "opus"

    def test_no_routing_uses_fixed_model(self):
        from inertia_forge.ignite_steps import resolve_model
        cfg = type("C", (), {"model": "fixed", "model_routing": None})()
        assert resolve_model({"complexity": 50}, cfg) == "fixed"
