"""v0.6.0 — timer, cache, subagent, template, migrate, mcp (all full)."""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestTimer:
    def test_lifecycle(self, proj: Path) -> None:
        from inertia_forge import timer
        assert timer.start("build") is True
        assert timer.start("again") is False          # one active at a time
        assert timer.active()["label"] == "build"
        rec = timer.stop()
        assert rec["label"] == "build" and rec["duration"] >= 0
        assert "build" in timer.totals()


class TestCache:
    def test_set_get_rm(self, proj: Path) -> None:
        from inertia_forge import cache
        cache.set_blob("ctx/1", "hello world")
        assert cache.get_blob("ctx/1") == "hello world"
        assert cache.has("ctx/1")
        assert cache.get_blob("missing") is None
        assert main(["cache", "list"]) == 0


class TestSubagent:
    def test_create_parse_validate(self, proj: Path) -> None:
        from inertia_forge import subagent as sa
        sa.create("reviewer", "reviews code", "Read, Grep", "You review code.")
        d = sa.parse("reviewer")
        assert d["description"] == "reviews code" and d["tools"] == "Read, Grep"
        assert "reviewer" in sa.list_agents()
        assert sa.validate_agent("reviewer") == []


class TestTemplate:
    def test_scaffold(self, proj: Path) -> None:
        dest = proj / "newproj"
        assert main(["template", "new", str(dest)]) == 0
        assert (dest / "forge_skills.yaml").exists()
        assert (dest / ".pre-commit-config.yaml").exists()
        assert (dest / "tests" / "test_smoke.py").exists()


class TestMigrate:
    def test_versioning(self, proj: Path) -> None:
        from inertia_forge import migrate as m
        assert m.current_version() == 0
        assert len(m.pending()) >= 1
        applied = m.run()
        assert applied and m.current_version() == m.SCHEMA_VERSION
        assert m.pending() == []


class TestMcp:
    def test_initialize_and_list(self, proj: Path) -> None:
        from inertia_forge.mcp import handle
        init = handle({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        assert init["result"]["serverInfo"]["name"] == "inertia-forge"
        tl = handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        assert len(tl["result"]["tools"]) >= 5

    def test_notification_no_response(self, proj: Path) -> None:
        from inertia_forge.mcp import handle
        assert handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None

    def test_tool_call(self, proj: Path) -> None:
        from inertia_forge.mcp import handle
        r = handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                    "params": {"name": "forge_skills", "arguments": {}}})
        text = r["result"]["content"][0]["text"]
        assert "implementing_with_tdd" in text
