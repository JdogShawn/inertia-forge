"""v0.2.0: doctor, sweep, scan-deps, skills export, gate audit logging."""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge.cli import main


def _rules(findings: list[dict]) -> set[str]:
    return {f["rule"] for f in findings}


class TestSweep:
    def test_flags_unused_keeps_used(self, tmp_path: Path) -> None:
        from inertia_forge.sweep import find_unused_imports
        f = tmp_path / "m.py"
        f.write_text("import os\nimport sys\nprint(os.getcwd())\n", encoding="utf-8")
        msgs = [x["message"] for x in find_unused_imports(f)]
        assert any("sys" in m for m in msgs) and not any("import os" in m for m in msgs)

    def test_respects_all_and_noqa(self, tmp_path: Path) -> None:
        from inertia_forge.sweep import find_unused_imports
        f = tmp_path / "m.py"
        f.write_text("import os  # noqa\nimport re\n__all__ = ['re']\n", encoding="utf-8")
        assert find_unused_imports(f) == []

    def test_fix_removes_unused(self, tmp_path: Path) -> None:
        f = tmp_path / "m.py"
        f.write_text("import os\nimport sys\nx = sys.argv\n", encoding="utf-8")
        assert main(["sweep", "--fix", str(f)]) == 0
        assert "import os" not in f.read_text(encoding="utf-8")


class TestDoctor:
    def test_healthy_project_passes(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".forge").mkdir()
        assert main(["doctor"]) == 0   # no FAIL checks

    def test_fix_creates_forge_dir(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        assert main(["doctor", "--fix"]) == 0
        assert (tmp_path / ".forge").is_dir()


class TestExport:
    def test_json_and_md(self, capsys) -> None:
        assert main(["skills", "export", "--format", "json"]) == 0
        assert "implementing_with_tdd" in capsys.readouterr().out
        assert main(["skills", "export", "--format", "md"]) == 0
        assert "##" in capsys.readouterr().out


class TestScanDeps:
    def test_graceful_int(self, tmp_path) -> None:
        from inertia_forge.commands import run_scan_deps
        rc = run_scan_deps([str(tmp_path)])
        assert isinstance(rc, int)   # never crashes, with or without pip-audit


class TestGateAuditLogging:
    def test_blocked_attempt_is_logged(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        from inertia_forge.bypass_prevention import read_behavioral_log
        from inertia_forge.hookutil import cmd_gate
        assert cmd_gate({"tool_input": {"command": "inertia-forge close"}}) == 2
        events = read_behavioral_log()
        assert any(e.get("type") == "gate_blocked" for e in events)
