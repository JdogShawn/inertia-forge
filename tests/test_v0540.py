"""v0.54.0 — the LLM-agnostic provider layer. The agent bridge builds commands
and parses output through provider adapters, so the whole forge runs on any LLM.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import providers
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestRegistry:
    def test_builtins_present(self) -> None:
        reg = providers.providers()
        for name in ("claude", "codex", "gemini", "ollama", "cursor-agent", "llm"):
            assert name in reg

    def test_yaml_override_and_add(self, proj: Path) -> None:
        (proj / ".forge" / "providers.yaml").write_text(
            "myllm:\n  command: [mycli, run, '{prompt}']\n  parse: text\n", encoding="utf-8")
        reg = providers.providers()
        assert reg["myllm"]["command"] == ["mycli", "run", "{prompt}"]


class TestBuildCommand:
    def test_claude_flags(self) -> None:
        cmd = providers.build_command("claude", "hi", model="opus",
                                      tools=["Read", "Bash"], cont=True, session_id="s1")
        assert cmd[:5] == ["claude", "-p", "hi", "--output-format", "json"]
        assert "--model" in cmd and "opus" in cmd and "Read,Bash" in cmd
        assert "--continue" in cmd and "s1" in cmd

    def test_codex_text(self) -> None:
        assert providers.build_command("codex", "do it") == ["codex", "exec", "do it"]

    def test_ollama_model_placeholder(self) -> None:
        cmd = providers.build_command("ollama", "hi", model="qwen3")
        assert cmd == ["ollama", "run", "qwen3", "hi"]

    def test_unknown_provider_falls_back_to_claude_shape(self) -> None:
        assert providers.build_command("nope", "hi")[0] == "claude"


class TestParse:
    def test_json(self) -> None:
        d = providers.parse("claude", '{"result":"ok","usage":{"input_tokens":3,'
                             '"output_tokens":4},"total_cost_usd":0.01,"modelUsage":{"m":{}}}')
        assert d["result"] == "ok" and d["output_tokens"] == 4 and d["model"] == "m"

    def test_text_provider_takes_stdout(self) -> None:
        assert providers.parse("codex", "plain answer")["result"] == "plain answer"

    def test_json_provider_plain_text_fallback(self) -> None:
        assert providers.parse("claude", "not json")["result"] == "not json"


class TestAgentUsesProviders:
    def test_session_builds_via_provider(self) -> None:
        from inertia_forge.agent import AgentSession
        cmd = AgentSession(agent="gemini", model="g3")._build_command("hi", cont=False)
        assert cmd[:3] == ["gemini", "-p", "hi"] and "g3" in cmd

    def test_parse_routes_text_provider(self) -> None:
        from inertia_forge.agent import _parse
        assert _parse("hello", "", 0, "codex").result == "hello"


class TestCli:
    def test_providers_list(self, proj: Path) -> None:
        assert main(["providers", "list"]) == 0

    def test_providers_show(self, proj: Path) -> None:
        assert main(["providers", "show", "claude"]) == 0
        assert main(["providers", "show", "nope"]) == 1
