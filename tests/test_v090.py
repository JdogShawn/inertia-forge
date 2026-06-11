"""v0.9.0 — command policy/sandbox, permission-denied audit, renamed slash commands."""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestSandbox:
    @pytest.mark.parametrize("cmd,tier", [
        ("rm -rf /", "blocked"),
        (":(){ :|:& };:", "blocked"),
        ("git reset --hard", "review"),
        ("rm -rf build", "review"),
        ("pytest -q", "allowed"),
        ("inertia-forge check .", "allowed"),
    ])
    def test_classify(self, proj: Path, cmd: str, tier: str) -> None:
        from inertia_forge.sandbox import classify
        assert classify(cmd) == tier

    def test_init_and_cli(self, proj: Path) -> None:
        assert main(["sandbox", "init"]) == 0
        assert (proj / ".forge" / "sandbox.yaml").exists()
        assert main(["sandbox", "status"]) == 0
        assert main(["sandbox", "check", "rm", "-rf", "/"]) == 2


class TestGateUsesSandbox:
    def test_catastrophic_blocked(self, proj: Path) -> None:
        from inertia_forge.hookutil import cmd_gate
        assert cmd_gate({"tool_input": {"command": "rm -rf /"}}) == 2
        assert cmd_gate({"tool_input": {"command": "pytest -q"}}) == 0


class TestPermissionDenied:
    def test_logs(self, proj: Path) -> None:
        from inertia_forge.bypass_prevention import read_behavioral_log
        from inertia_forge.hookutil import cmd_permission_denied
        assert cmd_permission_denied({"tool_name": "Bash", "reason": "user declined"}) == 0
        assert any(e.get("type") == "permission_denied" for e in read_behavioral_log())


class TestRenamedCommands:
    def test_motion_named_commands_installed(self, proj: Path) -> None:
        from inertia_forge import assets
        names = set(assets.install_commands(proj))
        assert {"ignite", "chart", "drive", "calibrate",
                "fortify", "prove", "trace", "map", "launch"} <= names
        assert not any(n.startswith("forge-") for n in names)   # no lazy names
