"""Claude Code hook helpers — the gate has no escape, the stop guard holds."""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import ForgeSkillBridge
from inertia_forge.hookutil import cmd_gate, cmd_stopguard


def _gate(command: str) -> int:
    return cmd_gate({"tool_input": {"command": command}})


class TestGate:
    @pytest.mark.parametrize("command", [
        "python -m inertia_forge.skill_bridge close",
        "inertia-forge close",
        "python -m inertia_forge.skill_bridge abandon src/",
        "rm src/.forge/active_x.json",
        "echo hi && inertia-forge close",          # no smuggling past `&&`
    ])
    def test_blocks_escape_commands(self, command: str) -> None:
        assert _gate(command) == 2

    @pytest.mark.parametrize("command", [
        "inertia-forge record-phase verify src/",
        "python -m inertia_forge.skill_bridge record-phase observe .",
        "pytest -q",
        "git status",
    ])
    def test_allows_legit_commands(self, command: str) -> None:
        assert _gate(command) == 0


class TestStopGuard:
    def test_blocks_stop_while_gates_remain(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / "src").mkdir()
        ForgeSkillBridge("investigating", "src", claude_session_id="A").start_session()
        assert cmd_stopguard({"session_id": "A"}) == 2

    def test_allows_stop_for_unrelated_tab(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / "src").mkdir()
        ForgeSkillBridge("investigating", "src", claude_session_id="A").start_session()
        # A different tab has no incomplete gates of its own.
        assert cmd_stopguard({"session_id": "OTHER"}) == 0

    def test_allows_stop_when_no_session(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        assert cmd_stopguard({"session_id": "A"}) == 0
