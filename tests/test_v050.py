"""v0.5.0 — containment (INERTIA's deterministic file-access tiers)."""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestContainment:
    def test_classify_tiers(self, proj: Path) -> None:
        from inertia_forge import containment as c
        cfg = {"active": True, "blocked": ["*.env", "secrets/*"], "readonly": ["CLAUDE.md"]}
        assert c.classify(".env", cfg) == "blocked"
        assert c.classify("secrets/key.txt", cfg) == "blocked"
        assert c.classify("CLAUDE.md", cfg) == "readonly"
        assert c.classify("src/app.py", cfg) == "readwrite"

    def test_inactive_allows_everything(self, proj: Path) -> None:
        from inertia_forge import containment as c
        cfg = {"active": False, "blocked": ["*.env"], "readonly": []}
        assert c.is_write_allowed(".env", cfg) is True

    def test_active_blocks_nonwritable(self, proj: Path) -> None:
        from inertia_forge import containment as c
        cfg = {"active": True, "blocked": ["*.env"], "readonly": ["CLAUDE.md"]}
        assert c.is_write_allowed(".env", cfg) is False
        assert c.is_write_allowed("CLAUDE.md", cfg) is False
        assert c.is_write_allowed("src/app.py", cfg) is True

    def test_hook_blocks_write(self, proj: Path) -> None:
        from inertia_forge.containment import save
        from inertia_forge.hookutil import cmd_contain
        save({"active": True, "blocked": [], "readonly": ["CLAUDE.md"]})
        assert cmd_contain({"tool_input": {"file_path": "CLAUDE.md"}}) == 2
        assert cmd_contain({"tool_input": {"file_path": "src/app.py"}}) == 0

    def test_cli_lifecycle(self, proj: Path, capsys) -> None:
        assert main(["contain", "set", "--readonly", "CLAUDE.md", "--blocked", "*.env"]) == 0
        assert main(["contain", "on"]) == 0
        assert main(["contain", "check", ".env"]) == 0
        assert "BLOCKED" in capsys.readouterr().out
        assert main(["contain", "status"]) == 0
        assert main(["contain", "off"]) == 0
        from inertia_forge import containment as c
        assert c.load()["active"] is False
