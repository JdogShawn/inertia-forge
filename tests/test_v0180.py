"""v0.18.0 — structured JSON output (envelope + `json` front door), composite
preflight readiness gate, store-integrity validation, finding dedup. Deterministic.
"""
from __future__ import annotations

import json as _json
from pathlib import Path

import pytest

from inertia_forge import envelope, preflight, storecheck
from inertia_forge import tasks as t
from inertia_forge.cli import main
from inertia_forge.commands import _dedup_findings


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestEnvelope:
    def test_wrap_shapes(self) -> None:
        assert envelope.wrap_ok({"x": 1}) == {"status": "ok", "data": {"x": 1}, "errors": []}
        e = envelope.wrap_error("boom")
        assert e["status"] == "error" and e["errors"] == ["boom"]

    def test_emit_exit_codes(self, capsys) -> None:
        assert envelope.emit(envelope.wrap_ok([])) == 0
        assert envelope.emit(envelope.wrap_error("x")) == 1


class TestJsonCommand:
    def test_graph_is_valid_envelope(self, proj, capsys) -> None:
        t.add_task("T1.1", "a", 5, ["x"], "pytest")
        t.add_task("T1.2", "b", 3, ["y"], "pytest", depends_on=["T1.1"])
        assert main(["json", "graph"]) == 0
        out = _json.loads(capsys.readouterr().out)
        assert out["status"] == "ok"
        assert out["data"]["ready"] == ["T1.1"]
        assert out["data"]["blocked"] == {"T1.2": ["T1.1"]}

    def test_consistency_error_status_on_drift(self, proj, capsys) -> None:
        t.add_task("T1.1", "a", 5, ["x"], "pytest", depends_on=["T1.1"])  # self-dep
        assert main(["json", "consistency"]) == 1
        out = _json.loads(capsys.readouterr().out)
        assert out["status"] == "error" and out["errors"]

    def test_status_query(self, proj, capsys) -> None:
        t.create_plan("feature", "demo")
        assert main(["json", "status"]) == 0
        out = _json.loads(capsys.readouterr().out)
        assert out["data"]["plan"]["title"] == "demo"


class TestStoreCheck:
    def test_clean_store(self, proj) -> None:
        t.add_task("T1.1", "a", 5, ["x"], "pytest")
        assert storecheck.check_tasks() == []
        assert main(["validate-store"]) == 0

    def test_catches_bad_status_and_missing_field(self, proj) -> None:
        t.add_task("T1.1", "a", 5, ["x"], "pytest")
        store = Path(".forge/forge_tasks.json")
        data = _json.loads(store.read_text(encoding="utf-8"))
        data["tasks"]["T1.1"]["status"] = "bogus"
        del data["tasks"]["T1.1"]["verification"]
        store.write_text(_json.dumps(data), encoding="utf-8")
        issues = storecheck.check_tasks()
        assert any("invalid status" in i for i in issues)
        assert any("missing field 'verification'" in i for i in issues)
        assert main(["validate-store"]) == 1

    def test_invalid_json(self, proj) -> None:
        Path(".forge/forge_tasks.json").write_text("{not json", encoding="utf-8")
        assert any("invalid JSON" in i for i in storecheck.check_tasks())


class TestPreflight:
    def test_missing_arch_path_warns_not_fails(self, proj, capsys) -> None:
        assert preflight._check_arch("nonexistent")[1] == "WARN"

    def test_fails_on_consistency_drift(self, proj) -> None:
        t.add_task("T1.1", "a", 5, ["x"], "pytest", depends_on=["T9.9"])  # missing dep
        assert main(["preflight", "--path", "nonexistent"]) == 1

    def test_passes_when_clean(self, proj, monkeypatch) -> None:
        monkeypatch.setattr("inertia_forge.gitcheck.dirty_files", lambda root: [])
        t.create_plan("feature", "demo")
        t.add_task("T1.1", "a", 5, ["x"], "pytest")
        assert main(["preflight", "--path", "nonexistent"]) == 0  # only WARNs


class TestDedup:
    def test_collapses_identical(self) -> None:
        f = [{"severity": "P0", "message": "dup"}, {"severity": "P0", "message": "dup"},
             {"severity": "P1", "message": "other"}]
        out = _dedup_findings(f)
        assert len(out) == 2 and out[0]["message"] == "dup"
