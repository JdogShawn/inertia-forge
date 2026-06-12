"""v0.27.0 — test-coverage gate (Cobertura XML parse + threshold). Hermetic:
synthetic coverage.xml written to tmp.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import coverage
from inertia_forge.cli import main

_XML = """<coverage line-rate="0.82">
  <packages><package><classes>
    <class filename="a.py" line-rate="0.95"/>
    <class filename="b.py" line-rate="0.40"/>
  </classes></package></packages>
</coverage>
"""


class TestParse:
    def test_total_and_files(self, tmp_path: Path) -> None:
        f = tmp_path / "coverage.xml"
        f.write_text(_XML, encoding="utf-8")
        total, files = coverage.parse_coverage(f)
        assert round(total, 1) == 82.0
        assert dict(files) == {"a.py": pytest.approx(95.0), "b.py": pytest.approx(40.0)}

    def test_bad_xml(self, tmp_path: Path) -> None:
        f = tmp_path / "coverage.xml"
        f.write_text("<not valid", encoding="utf-8")
        assert coverage.parse_coverage(f) == (None, [])


class TestCli:
    def _xml(self, tmp_path: Path) -> Path:
        f = tmp_path / "coverage.xml"
        f.write_text(_XML, encoding="utf-8")
        return f

    def test_total_gate(self, tmp_path: Path, monkeypatch) -> None:
        f = self._xml(tmp_path)
        assert main(["coverage", str(f), "--min", "80"]) == 0   # 82 >= 80
        assert main(["coverage", str(f), "--min", "90"]) == 1   # 82 < 90

    def test_per_file_gate(self, tmp_path: Path) -> None:
        f = self._xml(tmp_path)
        # total passes, but b.py (40%) is below per-file 60 -> fail
        assert main(["coverage", str(f), "--min", "80", "--per-file", "60"]) == 1
        assert main(["coverage", str(f), "--min", "80", "--per-file", "30"]) == 0

    def test_missing_report_is_advisory(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        assert main(["coverage", "nope.xml"]) == 0
