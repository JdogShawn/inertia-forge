"""v0.44.0 — release checklist is now a real readiness gate: versions, clean
tree, CHANGELOG entry, tests collectable, doc freshness. subprocess/git mocked.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import release
from inertia_forge.cli import main


class _R:
    returncode = 0


@pytest.fixture()
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('version = "1.0.0"\n', encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text('__version__ = "1.0.0"\n', encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("## 1.0.0\nnotes\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("readme", encoding="utf-8")
    monkeypatch.setattr("inertia_forge.gitcheck.dirty_files", lambda r: [])
    monkeypatch.setattr("subprocess.run", lambda *a, **k: _R())
    return tmp_path


class TestReleaseChecks:
    def test_all_pass(self, project: Path) -> None:
        checks = release._release_checks()
        names = [n for n, _, _ in checks]
        assert names == ["versions", "git", "changelog", "tests", "docs"]
        status = {n: s for n, s, _ in checks}
        assert status["versions"] == "PASS" and status["changelog"] == "PASS"
        assert status["tests"] == "PASS"

    def test_version_mismatch_fails(self, project: Path) -> None:
        (project / "src" / "__init__.py").write_text('__version__ = "2.0.0"\n', encoding="utf-8")
        status = {n: s for n, s, _ in release._release_checks()}
        assert status["versions"] == "FAIL"

    def test_missing_changelog_entry_fails(self, project: Path) -> None:
        (project / "CHANGELOG.md").write_text("## 0.0.1\nold\n", encoding="utf-8")
        status = {n: s for n, s, _ in release._release_checks()}
        assert status["changelog"] == "FAIL"  # no 1.0.0 entry

    def test_no_changelog_file_warns(self, project: Path) -> None:
        (project / "CHANGELOG.md").unlink()
        status = {n: s for n, s, _ in release._release_checks()}
        assert status["changelog"] == "WARN"

    def test_no_tests_warns_not_fails(self, project: Path, monkeypatch) -> None:
        class _NoTests:
            returncode = 5  # pytest "no tests collected"
        monkeypatch.setattr("subprocess.run", lambda *a, **k: _NoTests())
        status = {n: s for n, s, _ in release._release_checks()}
        assert status["tests"] == "WARN"

    def test_cli_gate(self, project: Path) -> None:
        assert main(["release", "checklist"]) == 0           # all pass/warn
        (project / "src" / "__init__.py").write_text('__version__ = "9.9.9"\n', encoding="utf-8")
        assert main(["release", "checklist"]) == 1           # version mismatch blocks
