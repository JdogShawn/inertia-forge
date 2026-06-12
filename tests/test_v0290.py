"""v0.29.0 — declarative QC runner, MCP server wired with the gated tools +
analysis suite, and the Crucible QC agent. Deterministic.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import assets, qc
from inertia_forge.cli import main
from inertia_forge.mcp import handle


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestQCRunner:
    def test_file_steps(self, proj: Path) -> None:
        (proj / "a.txt").write_text("hello world", encoding="utf-8")
        suite = {"scenarios": [
            {"name": "files", "steps": [
                {"file_exists": "a.txt"},
                {"file_contains": {"path": "a.txt", "text": "world"}}]},
            {"name": "missing", "steps": [{"file_exists": "nope.txt"}]}]}
        results = qc.run_suite(suite)
        assert results[0][1] == "passed"
        assert results[1][1] == "failed" and results[1][2]

    def test_run_step_exit_ok(self, proj: Path) -> None:
        suite = {"scenarios": [{"name": "s", "steps": [{"run": "skills", "expect_exit": 0}]}]}
        assert qc.run_suite(suite)[0][1] == "passed"

    def test_run_step_expect_contains_fail(self, proj: Path) -> None:
        suite = {"scenarios": [{"name": "s",
                 "steps": [{"run": "skills", "expect_contains": "ZZZ_NOT_THERE"}]}]}
        name, verdict, failures = qc.run_suite(suite)[0]
        assert verdict == "failed" and "missing" in failures[0]

    def test_cli_pass_fail_missing(self, proj: Path) -> None:
        good = proj / "g.qc.yaml"
        good.write_text("scenarios:\n  - name: ok\n    steps:\n      - file_exists: g.qc.yaml\n",
                        encoding="utf-8")
        bad = proj / "b.qc.yaml"
        bad.write_text("scenarios:\n  - name: bad\n    steps:\n      - file_exists: nope\n",
                       encoding="utf-8")
        assert main(["qc", str(good)]) == 0
        assert main(["qc", str(bad)]) == 1
        assert main(["qc", "missing.yaml"]) == 1


class TestMcpWiring:
    def test_tools_list_has_gated_and_analysis(self) -> None:
        resp = handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        names = {t["name"] for t in resp["result"]["tools"]}
        assert {"forge_run", "forge_write", "forge_edit", "forge_view", "forge_qc",
                "forge_vet", "forge_review", "forge_imports", "forge_json"} <= names

    def test_gated_view_via_mcp(self, proj: Path) -> None:
        (proj / "r.txt").write_text("visible-content", encoding="utf-8")
        resp = handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                       "params": {"name": "forge_view", "arguments": {"path": "r.txt"}}})
        assert "visible-content" in resp["result"]["content"][0]["text"]

    def test_blocked_run_refused_via_mcp(self, proj: Path, monkeypatch) -> None:
        monkeypatch.setattr("inertia_forge.sandbox.classify", lambda c, p=None: "blocked")
        resp = handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                       "params": {"name": "forge_run", "arguments": {"command": "rm -rf /"}}})
        assert "BLOCKED" in resp["result"]["content"][0]["text"]


class TestCrucibleAgent:
    def test_installed(self, tmp_path: Path) -> None:
        installed = assets.install_agents(tmp_path)
        assert any("crucible" in str(a).lower() for a in installed)
        text = (tmp_path / ".claude" / "agents" / "crucible.md").read_text(encoding="utf-8")
        assert "QC" in text and "Crucible" in text
