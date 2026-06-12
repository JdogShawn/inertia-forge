"""v0.28.0 — the forge's gated tool set (run/write/edit/view). Safety-critical:
a gate must NEVER auto-run a non-allowed command. subprocess is stubbed so no
real command executes.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import tools
from inertia_forge.cli import main


class _Proc:
    returncode = 0


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    ran = {"called": False}
    monkeypatch.setattr(tools.subprocess, "run",
                        lambda *a, **k: (ran.__setitem__("called", True), _Proc())[1])
    return tmp_path, ran, monkeypatch


class TestRun:
    def test_allowed_runs(self, proj) -> None:
        _, ran, mp = proj
        mp.setattr("inertia_forge.sandbox.classify", lambda c, p=None: "allowed")
        assert main(["run", "echo", "hi"]) == 0
        assert ran["called"] is True

    def test_blocked_never_runs(self, proj) -> None:
        _, ran, mp = proj
        mp.setattr("inertia_forge.sandbox.classify", lambda c, p=None: "blocked")
        assert main(["run", "rm", "-rf", "/"]) == 2
        assert ran["called"] is False  # the safety guarantee

    def test_review_refused_by_default(self, proj) -> None:
        _, ran, mp = proj
        mp.setattr("inertia_forge.sandbox.classify", lambda c, p=None: "review")
        assert main(["run", "git", "reset", "--hard"]) == 2
        assert ran["called"] is False

    def test_review_runs_with_flag(self, proj) -> None:
        _, ran, mp = proj
        mp.setattr("inertia_forge.sandbox.classify", lambda c, p=None: "review")
        assert main(["run", "--allow-review", "git", "reset", "--hard"]) == 0
        assert ran["called"] is True


class TestFileTools:
    def test_write_allowed(self, proj) -> None:
        tmp, _, mp = proj
        mp.setattr("inertia_forge.containment.is_write_allowed", lambda p, c=None: True)
        assert main(["write", "notes.txt", "--content", "hello"]) == 0
        assert (tmp / "notes.txt").read_text(encoding="utf-8") == "hello"

    def test_write_blocked_by_containment(self, proj) -> None:
        tmp, _, mp = proj
        mp.setattr("inertia_forge.containment.is_write_allowed", lambda p, c=None: False)
        mp.setattr("inertia_forge.containment.classify", lambda p, c=None: "blocked")
        assert main(["write", "secret.env", "--content", "K=1"]) == 2
        assert not (tmp / "secret.env").exists()  # never written

    def test_edit_exact_match(self, proj) -> None:
        tmp, _, mp = proj
        mp.setattr("inertia_forge.containment.is_write_allowed", lambda p, c=None: True)
        (tmp / "f.txt").write_text("alpha beta", encoding="utf-8")
        assert main(["edit", "f.txt", "--old", "alpha", "--new", "gamma"]) == 0
        assert (tmp / "f.txt").read_text(encoding="utf-8") == "gamma beta"

    def test_edit_non_unique_refused(self, proj) -> None:
        tmp, _, mp = proj
        mp.setattr("inertia_forge.containment.is_write_allowed", lambda p, c=None: True)
        (tmp / "f.txt").write_text("x x x", encoding="utf-8")
        assert main(["edit", "f.txt", "--old", "x", "--new", "y"]) == 1
        assert (tmp / "f.txt").read_text(encoding="utf-8") == "x x x"  # untouched

    def test_view_blocked(self, proj) -> None:
        tmp, _, mp = proj
        mp.setattr("inertia_forge.containment.classify", lambda p, c=None: "blocked")
        (tmp / "s.env").write_text("secret", encoding="utf-8")
        assert main(["view", "s.env"]) == 2

    def test_view_reads(self, proj, capsys) -> None:
        tmp, _, mp = proj
        mp.setattr("inertia_forge.containment.classify", lambda p, c=None: "readwrite")
        (tmp / "r.txt").write_text("visible", encoding="utf-8")
        assert main(["view", "r.txt"]) == 0
        assert "visible" in capsys.readouterr().out
