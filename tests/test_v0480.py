"""v0.48.0 — the agent client (optional LLM bridge). subprocess is fully mocked;
NO test ever invokes a real coding-agent CLI.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import agent
from inertia_forge.cli import main


class _Proc:
    def __init__(self, stdout: str, returncode: int = 0, stderr: str = ""):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


def _run(stdout: str, returncode: int = 0, stderr: str = ""):
    return lambda *a, **k: _Proc(stdout, returncode, stderr)


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestBuildCommand:
    def test_claude_with_flags(self) -> None:
        s = agent.AgentSession(model="claude-opus-4-8", allowed_tools=["Read", "Bash"])
        cmd = s._build_command("p", cont=False)
        assert cmd[:5] == ["claude", "-p", "p", "--output-format", "json"]
        assert "--model" in cmd and "claude-opus-4-8" in cmd and "Read,Bash" in cmd

    def test_continue_and_codex_and_permission(self) -> None:
        assert "--continue" in agent.AgentSession(session_id="s1")._build_command("p", cont=True)
        assert agent.AgentSession(agent="codex")._build_command("p", False) == ["codex", "exec", "p"]
        assert "--permission-mode" in agent.AgentSession(permission_mode="plan")._build_command("p", False)


class TestParse:
    def test_json(self) -> None:
        r = agent._parse('{"result":"ok","usage":{"input_tokens":10,"output_tokens":5},'
                         '"total_cost_usd":0.02,"session_id":"s","modelUsage":{"m":{}}}', "", 0)
        assert r.result == "ok" and r.total_tokens == 15 and r.cost_usd == 0.02 and r.model == "m"

    def test_plain_text(self) -> None:
        assert agent._parse("plain output", "", 0).result == "plain output"

    def test_nonzero_exit_is_error(self) -> None:
        r = agent._parse("", "boom", 1)
        assert r.is_error and r.error == "boom"

    def test_is_error_field(self) -> None:
        r = agent._parse('{"is_error":true,"error":"nope","result":""}', "", 0)
        assert r.is_error and r.error == "nope"


class TestSession:
    def test_accumulates_cost_and_tokens(self, proj: Path, monkeypatch) -> None:
        monkeypatch.setattr(agent.subprocess, "run",
                            _run('{"result":"x","usage":{"input_tokens":10,"output_tokens":5},'
                                 '"total_cost_usd":0.01}'))
        s = agent.AgentSession()
        r = s.invoke("p")
        assert r.result == "x" and s.invocations == 1 and s.total_tokens == 15 and s.total_cost == 0.01

    def test_token_budget_blocks(self, proj: Path) -> None:
        s = agent.AgentSession(token_budget=10)
        s.total_tokens = 10
        r = s.invoke("p")
        assert r.is_error and "budget" in r.error

    def test_cli_not_found_is_clean(self, proj: Path, monkeypatch) -> None:
        def boom(*a, **k):
            raise FileNotFoundError()
        monkeypatch.setattr(agent.subprocess, "run", boom)
        r = agent.AgentSession().invoke("p")
        assert r.is_error and "not found" in r.error

    def test_continue_requires_session(self) -> None:
        with pytest.raises(ValueError):
            agent.AgentSession().continue_session("p")


class TestTypeStats:
    """The full per-type calibration record — std_dev, p80, success rate,
    cx/min, recommended tier/model/effort, MAPE."""

    def test_full_record(self, proj: Path) -> None:
        from inertia_forge import calibrate
        for actual in (60_000, 80_000, 80_000):
            calibrate.record(50_000, actual, task_type="refactor",
                             duration_seconds=2400, outcome="success", complexity=55)
        calibrate.record(50_000, 80_000, task_type="refactor",
                         duration_seconds=2400, outcome="fail", complexity=55)
        s = calibrate.type_stats("refactor", "openai")
        assert s["sample_count"] == 4
        assert s["avg_tokens"] == 75_000.0
        assert s["std_dev"] > 0 and s["p80_tokens"] >= s["avg_tokens"]
        assert s["success_rate"] == 75.0                 # 3 of 4 success
        assert s["recommended_tier"] == "frontier"        # >60K tokens
        assert s["recommended_model"] == "gpt-5.5"
        assert s["recommended_effort"] == "high"          # complexity 55 > 40
        assert s["cx_per_minute"] is not None

    def test_effort_for_type(self) -> None:
        from inertia_forge import calibrate
        assert calibrate.effort_for_type("test") == "low"
        assert calibrate.effort_for_type("refactor") == "high"
        assert calibrate.effort_for_type("unknown") == "medium"

    def test_none_when_empty(self, proj: Path) -> None:
        from inertia_forge import calibrate
        assert calibrate.type_stats("ghost") is None

    def test_cli_stats_and_record_flags(self, proj: Path) -> None:
        calibrate_main = main
        assert calibrate_main(["calibrate", "record", "--estimated", "50000",
                               "--actual", "70000", "--type", "feature",
                               "--duration", "1800", "--outcome", "success",
                               "--complexity", "60"]) == 0
        assert calibrate_main(["calibrate", "stats", "--type", "feature",
                               "--family", "anthropic"]) == 0
        assert calibrate_main(["calibrate", "stats", "--type", "ghost"]) == 0  # no data, clean


class TestCli:
    def test_invoke_json(self, proj: Path, monkeypatch, capsys) -> None:
        monkeypatch.setattr(agent.subprocess, "run",
                            _run('{"result":"hi","usage":{"input_tokens":1,"output_tokens":2}}'))
        import json
        assert main(["invoke", "do it", "--json"]) == 0
        assert json.loads(capsys.readouterr().out)["result"] == "hi"

    def test_invoke_error_exit(self, proj: Path, monkeypatch) -> None:
        monkeypatch.setattr(agent.subprocess, "run", _run("", 1, "failed"))
        assert main(["invoke", "do it"]) == 1
