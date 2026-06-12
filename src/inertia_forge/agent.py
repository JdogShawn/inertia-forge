"""Agent client — the forge's single optional bridge to a coding-agent CLI.

The deterministic core is zero-LLM and never calls a model. This module is the
ONE explicit, opt-in exception: a headless client for an installed coding agent.
It is **LLM-agnostic** — the invocation is defined by a provider adapter (see
:mod:`providers`), so the same session runs on any configured LLM CLI (Claude,
Codex, Gemini, Cursor, Ollama, …), not a single vendor. It runs a prompt, parses
the structured result, accumulates cost/tokens across a session, can continue a
session, and can be capped by a token budget. Each call is recorded to telemetry.
Requires the chosen CLI on PATH — absent, every call fails cleanly. Nothing in
the deterministic core imports this.
"""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

_MAX_PROMPT = 100_000
# Tool presets — a driver writes code; a navigator also plans (Skill). Agent is
# excluded everywhere to prevent unbounded sub-agent recursion.
DRIVER_TOOLS = ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
NAVIGATOR_TOOLS = DRIVER_TOOLS + ["Skill"]


@dataclass
class AgentResponse:
    result: str = ""
    session_id: str | None = None
    cost_usd: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    is_error: bool = False
    error: str | None = None
    duration_seconds: float = 0.0
    model: str = "unknown"
    raw_output: str = ""

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict:
        return {"session_id": self.session_id, "result": self.result, "cost_usd": self.cost_usd,
                "tokens": {"input": self.input_tokens, "output": self.output_tokens,
                           "total": self.total_tokens},
                "is_error": self.is_error, "error": self.error, "model": self.model,
                "duration_seconds": self.duration_seconds}


def _parse(stdout: str, stderr: str, returncode: int, provider: str = "claude") -> AgentResponse:
    if returncode != 0:
        return AgentResponse(is_error=True, error=stderr.strip() or f"exit {returncode}", raw_output=stdout)
    from inertia_forge import providers
    d = providers.parse(provider, stdout)
    return AgentResponse(
        result=d["result"], session_id=d["session_id"], cost_usd=d["cost_usd"],
        input_tokens=d["input_tokens"], output_tokens=d["output_tokens"],
        is_error=d["is_error"], error=d["error"], model=d["model"], raw_output=stdout)


def _record(agent: str, resp: AgentResponse) -> None:
    try:
        from inertia_forge import telemetry
        telemetry.record("invoke", agent, float(resp.output_tokens),
                         {"model": resp.model, "cost_usd": resp.cost_usd,
                          "in": resp.input_tokens, "error": resp.is_error})
    except Exception:
        pass


@dataclass
class AgentSession:
    agent: str = "claude"
    model: str | None = None
    allowed_tools: list[str] | None = None
    permission_mode: str = "auto"
    working_dir: Path | None = None
    timeout_seconds: int = 1800
    token_budget: int | None = None
    session_id: str | None = field(default=None)
    invocations: int = field(default=0)
    total_cost: float = field(default=0.0)
    total_tokens: int = field(default=0)

    def invoke(self, prompt: str) -> AgentResponse:
        return self._execute(prompt, cont=False)

    def continue_session(self, prompt: str) -> AgentResponse:
        if not self.session_id:
            raise ValueError("no session to continue — call invoke() first")
        return self._execute(prompt, cont=True)

    def terminate(self) -> None:
        self.session_id = None

    def _build_command(self, prompt: str, cont: bool) -> list[str]:
        if len(prompt) > _MAX_PROMPT:
            prompt = prompt[:_MAX_PROMPT] + "\n\n[TRUNCATED — prompt exceeded maximum length]"
        from inertia_forge import providers
        return providers.build_command(
            self.agent, prompt, model=self.model, tools=self.allowed_tools,
            permission_mode=self.permission_mode, session_id=self.session_id, cont=cont)

    def _execute(self, prompt: str, cont: bool) -> AgentResponse:
        start = time.time()
        if self.token_budget is not None and self.total_tokens >= self.token_budget:
            return AgentResponse(is_error=True, error=f"token budget {self.token_budget} exhausted")
        try:
            r = subprocess.run(self._build_command(prompt, cont),
                               cwd=str(self.working_dir) if self.working_dir else None,
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=self.timeout_seconds)
        except subprocess.TimeoutExpired:
            return AgentResponse(is_error=True, error=f"timed out after {self.timeout_seconds}s",
                                 duration_seconds=round(time.time() - start, 2))
        except FileNotFoundError:
            return AgentResponse(is_error=True, error=f"'{self.agent}' CLI not found on PATH — is it installed?")
        except OSError as e:
            return AgentResponse(is_error=True, error=str(e))
        resp = _parse(r.stdout, r.stderr, r.returncode, self.agent)
        resp.duration_seconds = round(time.time() - start, 2)
        if resp.session_id:
            self.session_id = resp.session_id
        self.invocations += 1
        self.total_cost += resp.cost_usd
        self.total_tokens += resp.total_tokens
        _record(self.agent, resp)
        return resp


def run_invoke(argv: list[str]) -> int:
    import argparse
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge invoke")
    p.add_argument("prompt")
    p.add_argument("--agent", default="claude",
                   help="provider name (see `inertia-forge providers list`)")
    p.add_argument("--model", default=None)
    p.add_argument("--allow-tools", nargs="*", default=None)
    p.add_argument("--driver", action="store_true", help="use the driver tool preset")
    p.add_argument("--permission-mode", default="auto")
    p.add_argument("--timeout", type=int, default=1800)
    p.add_argument("--json", action="store_true", help="emit the full structured result")
    args = p.parse_args(argv)
    tools = DRIVER_TOOLS if args.driver else args.allow_tools
    session = AgentSession(agent=args.agent, model=args.model, allowed_tools=tools,
                           permission_mode=args.permission_mode, timeout_seconds=args.timeout)
    resp = session.invoke(args.prompt)
    if args.json:
        print(json.dumps(resp.to_dict(), indent=2))
    elif resp.is_error:
        print(f"{seal('error')} {resp.error}")
    else:
        print(resp.result)
    return 1 if resp.is_error else 0
