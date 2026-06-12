"""v0.14.0 — Claude Code statusLine segment (⚛ INERTIA forge · state).

The statusline reads Claude's status JSON from stdin and prints one branded
line; it forces colour on (Claude Code renders ANSI off-TTY) and never crashes.
`init` wires it into .claude/settings.json, respecting any custom statusLine.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from inertia_forge import palette, statusline
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestRender:
    def test_carries_brand_and_ready(self, proj: Path) -> None:
        line = palette.strip_ansi(statusline.render({"session_id": "s1"}))
        assert "INERTIA" in line and "forge" in line and "ready" in line

    def test_active_task_shows_in_segment(self, proj: Path) -> None:
        from inertia_forge import tasks as tk
        tk.add_task("T1.1", "do a thing", 3, ["a"], "pytest")
        tk.start_task("T1.1")
        line = palette.strip_ansi(statusline.render({"session_id": "s1"}))
        assert "T1.1" in line and "0/1" in line

    def test_never_crashes_on_garbage_payload(self, proj: Path) -> None:
        assert "INERTIA" in palette.strip_ansi(statusline.render({}))


class TestCli:
    def test_statusline_reads_stdin(self, proj: Path, monkeypatch, capsys) -> None:
        payload = json.dumps({"session_id": "abc", "model": {"display_name": "Opus 4.8"}})
        monkeypatch.setattr("sys.stdin", io.StringIO(payload))
        assert main(["statusline"]) == 0
        assert "INERTIA" in palette.strip_ansi(capsys.readouterr().out)

    def test_statusline_forces_color(self, proj: Path, monkeypatch, capsys) -> None:
        monkeypatch.setattr("sys.stdin", io.StringIO('{"session_id":"x"}'))
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setattr(palette, "_TRUECOLOR", None)
        main(["statusline"])
        # off-TTY but ANSI emitted because the statusline forces FORCE_COLOR
        assert "\x1b[" in capsys.readouterr().out

    def test_no_color_still_wins(self, proj: Path, monkeypatch, capsys) -> None:
        monkeypatch.setattr("sys.stdin", io.StringIO('{"session_id":"x"}'))
        monkeypatch.setenv("NO_COLOR", "1")
        monkeypatch.setattr(palette, "_TRUECOLOR", None)
        main(["statusline"])
        assert "\x1b[" not in capsys.readouterr().out


class TestInitWiring:
    def test_init_installs_statusline(self, proj: Path) -> None:
        assert main(["init", "--target", str(proj)]) == 0
        settings = json.loads((proj / ".claude" / "settings.json").read_text(encoding="utf-8"))
        sl = settings.get("statusLine")
        assert sl and sl["type"] == "command" and "statusline" in sl["command"]

    def test_init_respects_custom_statusline(self, proj: Path) -> None:
        claude = proj / ".claude"
        claude.mkdir()
        (claude / "settings.json").write_text(
            json.dumps({"statusLine": {"type": "command", "command": "my-own-bar"}}),
            encoding="utf-8")
        main(["init", "--target", str(proj)])
        settings = json.loads((claude / "settings.json").read_text(encoding="utf-8"))
        assert settings["statusLine"]["command"] == "my-own-bar"  # not clobbered
