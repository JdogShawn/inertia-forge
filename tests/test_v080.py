"""v0.8.0 — agent memory, slash commands, rules, scaffold, secret-allowlist, capabilities."""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestMemory:
    def test_add_show_list(self, proj: Path, capsys) -> None:
        from inertia_forge import memory
        assert main(["memory", "add", "piston", "always run arch after refactor", "--tag", "tdd"]) == 0
        assert "arch after refactor" in memory.show("piston")
        assert "piston" in memory.agents_with_memory()
        assert main(["memory", "list"]) == 0


class TestFullInit:
    def test_installs_everything(self, tmp_path: Path) -> None:
        assert main(["init", "--target", str(tmp_path)]) == 0
        c = tmp_path / ".claude"
        assert (c / "agents" / "piston.md").exists()
        assert (c / "skills" / "reviewing-code" / "SKILL.md").exists()
        assert (c / "commands" / "drive.md").exists()
        assert (c / "rules" / "architecture.md").exists()
        assert (c / "agent-memory" / "vector" / "MEMORY.md").exists()
        assert (tmp_path / "CLAUDE.md").exists()
        assert (tmp_path / ".forge" / "context" / "project.md").exists()

    def test_never_overwrites_claude_md(self, tmp_path: Path) -> None:
        (tmp_path / "CLAUDE.md").write_text("MY RULES", encoding="utf-8")
        main(["init", "--target", str(tmp_path)])
        assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == "MY RULES"


class TestSecretAllowlist:
    def test_allowlist_suppresses(self, proj: Path) -> None:
        from inertia_forge.commands import _scan_secrets
        f = proj / "conf.env"
        f.write_text('API_KEY = "dummyexamplevalue123"  # example\n', encoding="utf-8")
        assert len(_scan_secrets(f)) == 1                       # flagged by default
        (proj / ".forge" / "secret-allowlist.txt").write_text(
            "dummyexamplevalue123\n", encoding="utf-8")
        assert _scan_secrets(f) == []                           # now suppressed


class TestCapabilities:
    def test_manifest_and_cli(self, proj: Path, capsys) -> None:
        from inertia_forge.capabilities import manifest
        m = manifest()
        assert m["llm_calls"] == 0 and m["deterministic"] is True
        assert "piston" in m["agents"] and "task_management" in m["evidence_modes"]
        assert main(["capabilities"]) == 0
        assert main(["capabilities", "--json"]) == 0
