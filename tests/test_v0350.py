"""v0.35.0 — flaky-QC detection + orphaned __all__ export detection.
Deterministic: per-scenario QC history in telemetry; AST export integrity.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import deadcode, query, telemetry
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestFlaky:
    def test_detects_mixed_pass_fail(self, proj: Path) -> None:
        telemetry.record("qc_scenario", "login", 1.0)
        telemetry.record("qc_scenario", "login", 0.0)
        telemetry.record("qc_scenario", "stable", 1.0)
        telemetry.record("qc_scenario", "stable", 1.0)
        rows = {n: r for n, r, _ in query.flaky()}
        assert rows.get("login") == 50.0
        assert "stable" not in rows  # always passed → not flaky

    def test_cli_exit_1_when_flaky(self, proj: Path) -> None:
        telemetry.record("qc_scenario", "x", 1.0)
        telemetry.record("qc_scenario", "x", 0.0)
        assert main(["query", "flaky"]) == 1

    def test_cli_clean(self, proj: Path) -> None:
        telemetry.record("qc_scenario", "x", 1.0)
        assert main(["query", "flaky"]) == 0

    def test_qc_run_records_per_scenario(self, proj: Path) -> None:
        suite = proj / "s.qc.yaml"
        suite.write_text("scenarios:\n  - name: only\n    steps:\n      - file_exists: s.qc.yaml\n",
                         encoding="utf-8")
        main(["qc", str(suite)])
        assert telemetry.events(kind="qc_scenario", name="only")[0]["value"] == 1.0


class TestOrphanExports:
    def test_detects_ghost(self, tmp_path: Path) -> None:
        (tmp_path / "m.py").write_text(
            'def real():\n    return 1\n__all__ = ["real", "ghost"]\n', encoding="utf-8")
        names = [n for _, n in deadcode.orphan_exports(tmp_path)]
        assert "ghost" in names and "real" not in names

    def test_imported_name_is_valid_export(self, tmp_path: Path) -> None:
        (tmp_path / "m.py").write_text(
            'from os import path\n__all__ = ["path"]\n', encoding="utf-8")
        assert deadcode.orphan_exports(tmp_path) == []

    def test_module_var_is_valid_export(self, tmp_path: Path) -> None:
        (tmp_path / "m.py").write_text('VERSION = "1"\n__all__ = ["VERSION"]\n', encoding="utf-8")
        assert deadcode.orphan_exports(tmp_path) == []

    def test_cli_exits_1_on_broken_export(self, tmp_path: Path, monkeypatch) -> None:
        (tmp_path / "m.py").write_text('x = 1\n__all__ = ["x", "missing"]\n', encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        assert main(["dead-code", "."]) == 1  # broken export forces failure
