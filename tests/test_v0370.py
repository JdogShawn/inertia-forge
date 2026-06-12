"""v0.37.0 — QC enrichment (cross-referenced to the real qc/ schema): suite
validation, ${VAR} interpolation, discovery+tags, scaffold, preconditions,
verdicts (passed/failed/skipped), and the run/validate/list/init subcommands.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import qc, qc_suite
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestSchema:
    def test_valid(self) -> None:
        assert qc_suite.validate(
            {"scenarios": [{"name": "s", "steps": [{"file_exists": "x"}]}]}) == []

    def test_missing_fields(self) -> None:
        errs = qc_suite.validate({"scenarios": [{"steps": []}]})
        assert any("name" in e for e in errs) and any("steps" in e for e in errs)

    def test_no_scenarios(self) -> None:
        assert qc_suite.validate({"name": "x"})

    def test_unknown_step(self) -> None:
        errs = qc_suite.validate({"scenarios": [{"name": "s", "steps": [{"bogus": 1}]}]})
        assert any("unknown step" in e for e in errs)

    def test_interpolate(self, monkeypatch) -> None:
        monkeypatch.setenv("QC_URL", "http://x")
        resolved, unresolved = qc_suite.interpolate({"u": "${QC_URL}/p", "m": "${MISSING}"})
        assert resolved["u"] == "http://x/p" and unresolved == {"MISSING"}


class TestDiscovery:
    def test_discover_and_tag_filter(self, proj: Path) -> None:
        (proj / "a.qc.yaml").write_text("name: a\ntags: [smoke]\nscenarios: []\n", encoding="utf-8")
        (proj / "b.qc.yaml").write_text("name: b\ntags: [slow]\nscenarios: []\n", encoding="utf-8")
        assert len(qc_suite.discover(proj)) == 2
        assert len(qc_suite.discover(proj, ["smoke"])) == 1

    def test_scaffold(self, proj: Path) -> None:
        path = qc_suite.scaffold()
        assert path.exists() and "scenarios" in path.read_text(encoding="utf-8")


class TestRunner:
    def test_verdicts_with_skip_tags(self, proj: Path) -> None:
        suite = {"scenarios": [
            {"name": "a", "tags": ["core"], "steps": [{"file_exists": ".forge"}]},
            {"name": "b", "tags": ["slow"], "steps": [{"file_exists": ".forge"}]}]}
        verdicts = {n: v for n, v, _ in qc.run_suite(suite, skip_tags=["slow"])}
        assert verdicts == {"a": "passed", "b": "skipped"}

    def test_only_tags(self, proj: Path) -> None:
        suite = {"scenarios": [
            {"name": "a", "tags": ["core"], "steps": [{"file_exists": ".forge"}]},
            {"name": "b", "steps": [{"file_exists": ".forge"}]}]}
        verdicts = {n: v for n, v, _ in qc.run_suite(suite, only_tags=["core"])}
        assert verdicts == {"a": "passed", "b": "skipped"}

    def test_precondition_failure_detected(self, proj: Path) -> None:
        assert qc.check_preconditions({"preconditions": [{"file_exists": "nope"}]})
        assert qc.check_preconditions({"preconditions": [{"file_exists": ".forge"}]}) == []


class TestCli:
    def test_validate(self, proj: Path) -> None:
        good = proj / "g.qc.yaml"
        good.write_text("scenarios:\n  - name: s\n    steps:\n      - file_exists: g.qc.yaml\n",
                        encoding="utf-8")
        bad = proj / "b.qc.yaml"
        bad.write_text("scenarios:\n  - steps: []\n", encoding="utf-8")
        assert main(["qc", "validate", str(good)]) == 0
        assert main(["qc", "validate", str(bad)]) == 1

    def test_list_and_init(self, proj: Path) -> None:
        assert main(["qc", "init"]) == 0
        assert main(["qc", "list", ".forge"]) == 0

    def test_run_skip_tags_exit_0(self, proj: Path) -> None:
        suite = proj / "s.qc.yaml"
        suite.write_text(
            "scenarios:\n  - name: skipme\n    tags: [slow]\n    steps:\n      - file_exists: nope\n",
            encoding="utf-8")
        # the only failing scenario is skipped -> suite passes
        assert main(["qc", str(suite), "--skip-tags", "slow"]) == 0

    def test_backward_compatible_path_invocation(self, proj: Path) -> None:
        suite = proj / "s.qc.yaml"
        suite.write_text("scenarios:\n  - name: ok\n    steps:\n      - file_exists: s.qc.yaml\n",
                         encoding="utf-8")
        assert main(["qc", str(suite)]) == 0  # `qc <path>` still works
