"""v0.20.0 — deterministic code review (debug leftovers, markers, endpoints) +
structured diff view. Hermetic: planted files, git numstat parsed directly.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import diffstat, review
from inertia_forge.cli import main


class TestReview:
    def test_flags_real_debug_leftovers(self, tmp_path: Path) -> None:
        f = tmp_path / "a.py"
        f.write_text("import pdb\ndef g():\n    breakpoint()\n    pdb.set_trace()\n", encoding="utf-8")
        sev = [x["severity"] for x in review.review_file(f)]
        assert sev.count("P1") == 3  # import pdb + breakpoint + set_trace

    def test_does_not_flag_bare_print(self, tmp_path: Path) -> None:
        f = tmp_path / "cli.py"
        f.write_text("def main():\n    print('hello')\n    return 0\n", encoding="utf-8")
        assert review.review_file(f) == []  # a CLI prints by design

    def test_markers_and_endpoints_are_p2(self, tmp_path: Path) -> None:
        f = tmp_path / "n.py"
        f.write_text("x = 1  # TODO later\nhost = 'localhost'\n", encoding="utf-8")
        findings = review.review_file(f)
        assert {x["severity"] for x in findings} == {"P2"}
        joined = " ".join(x["message"] for x in findings)
        assert "TODO" in joined and "localhost" in joined

    def test_console_log_is_p1(self, tmp_path: Path) -> None:
        f = tmp_path / "x.js"
        f.write_text("console.log('debug')\n", encoding="utf-8")
        assert review.review_file(f)[0]["severity"] == "P1"

    def test_cli_exit_on_p1(self, tmp_path: Path, monkeypatch) -> None:
        (tmp_path / "bad.py").write_text("def f():\n    breakpoint()\n", encoding="utf-8")
        (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        assert main(["review", "bad.py"]) == 1
        assert main(["review", "ok.py"]) == 0


class TestDiff:
    def test_parse_numstat(self) -> None:
        rows = diffstat.parse_numstat("3\t1\tsrc/a.py\n0\t5\tREADME.md\n-\t-\tbin.dat\n")
        assert rows[0] == {"added": 3, "removed": 1, "path": "src/a.py"}
        assert rows[2] == {"added": 0, "removed": 0, "path": "bin.dat"}  # binary "-"

    def test_with_roles(self) -> None:
        rows = diffstat.with_roles([{"added": 1, "removed": 0, "path": "tests/test_x.py"}])
        assert rows[0]["role"] == "test"

    def test_cli_no_changes(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(diffstat, "git_numstat", lambda root, ref: "")
        assert main(["diff"]) == 0

    def test_cli_renders_changes(self, tmp_path: Path, monkeypatch, capsys) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(diffstat, "git_numstat", lambda root, ref: "2\t1\tsrc/a.py\n")
        assert main(["diff"]) == 0
        out = capsys.readouterr().out
        assert "src/a.py" in out and "+2" in out and "source" in out
