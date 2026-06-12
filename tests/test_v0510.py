"""v0.51.0 — dispatch a named agent (.claude/agents/<name>.md) through the
invoke bridge. AgentSession is mocked; no test invokes a real agent CLI.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import invoker
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".claude" / "agents").mkdir(parents=True)
    (tmp_path / ".forge").mkdir()
    return tmp_path


def _agent(proj: Path, name: str, fm: str = "", body: str = "You are the reviewer.") -> None:
    front = f"name: {name}\ndescription: a {name}\n{fm}"
    (proj / ".claude" / "agents" / f"{name}.md").write_text(
        f"---\n{front}---\n\n{body}\n", encoding="utf-8")


class _Resp:
    def __init__(self) -> None:
        self.result, self.is_error, self.error = "done", False, None

    def to_dict(self) -> dict:
        return {"result": self.result, "is_error": self.is_error}


class TestLoad:
    def test_load_def(self, proj: Path) -> None:
        _agent(proj, "nayru", fm="model: opus\npermissionMode: plan\ntools: Read, Grep\n")
        d = invoker.load_agent_def("nayru")
        assert d["model"] == "opus" and d["permission_mode"] == "plan"
        assert d["tools"] == ["Read", "Grep"] and "reviewer" in d["system_prompt"]

    def test_missing(self, proj: Path) -> None:
        assert invoker.load_agent_def("ghost") is None


class TestPrompt:
    def test_compose(self) -> None:
        out = invoker.build_agent_prompt("SYS", "CTX", prefix="PRE", suffix="SUF")
        assert out.index("PRE") < out.index("SYS") < out.index("SUF") < out.index("CTX")

    def test_handoff(self) -> None:
        pre = invoker.handoff_prefix("navigator", "the design")
        assert "Handoff from navigator" in pre and "the design" in pre


class TestDispatch:
    def test_dispatch_invokes_session(self, proj: Path, monkeypatch) -> None:
        _agent(proj, "driver", fm="model: sonnet\ntools: Read, Write\n")
        seen = {}

        class _Sess:
            def __init__(self, **kw):
                seen.update(kw)

            def invoke(self, prompt):
                seen["prompt"] = prompt
                return _Resp()
        monkeypatch.setattr("inertia_forge.agent.AgentSession", _Sess)
        resp = invoker.dispatch("driver", "build the widget")
        assert resp.result == "done"
        assert seen["model"] == "sonnet" and seen["allowed_tools"] == ["Read", "Write"]
        assert "build the widget" in seen["prompt"] and "You are the" in seen["prompt"]

    def test_dispatch_unknown_agent(self, proj: Path) -> None:
        resp = invoker.dispatch("ghost", "ctx")
        assert resp.is_error and "no such agent" in resp.error

    def test_handoff_dispatch(self, proj: Path, monkeypatch) -> None:
        _agent(proj, "fixer")
        captured = {}

        class _Sess:
            def __init__(self, **kw): ...
            def invoke(self, prompt):
                captured["prompt"] = prompt
                return _Resp()
        monkeypatch.setattr("inertia_forge.agent.AgentSession", _Sess)
        invoker.dispatch_with_handoff("fixer", "fix it", "nayru", "found a bug")
        assert "Handoff from nayru" in captured["prompt"] and "found a bug" in captured["prompt"]


class TestCli:
    def test_cli_dispatch(self, proj: Path, monkeypatch) -> None:
        _agent(proj, "driver")
        monkeypatch.setattr("inertia_forge.agent.AgentSession",
                            type("S", (), {"__init__": lambda s, **k: None,
                                           "invoke": lambda s, p: _Resp()}))
        assert main(["dispatch", "driver", "do it"]) == 0

    def test_cli_unknown(self, proj: Path) -> None:
        assert main(["dispatch", "ghost", "ctx"]) == 1
