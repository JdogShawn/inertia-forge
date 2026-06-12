"""Dispatch a named agent — `.claude/agents/<name>.md` → the invoke bridge.

The agent registry (CRUD/parse) lives in ``subagent``; this is the *invocation*
layer: load an agent's definition (its model, tools, permission mode, and system
prompt), prepend that system prompt to the caller's context, and run it through
``AgentSession``. One agent can hand off to another with prior context.

Still the one opt-in LLM bridge — the deterministic core never dispatches.
"""
from __future__ import annotations

from pathlib import Path


def load_agent_def(name: str) -> dict | None:
    """An agent's definition (name/description/model/permission/tools/body), or None."""
    from inertia_forge.subagent import parse
    d = parse(name)
    if d is None:
        return None
    tools = d.get("tools", "") or ""
    return {
        "name": d.get("name", name),
        "model": d.get("model") or None,
        "permission_mode": d.get("permissionMode") or d.get("permission_mode") or "auto",
        "tools": [t.strip() for t in tools.split(",") if t.strip()],
        "system_prompt": d.get("body", ""),
    }


def build_agent_prompt(system_prompt: str, context: str,
                       prefix: str = "", suffix: str = "") -> str:
    """Compose the dispatched prompt: [prefix] system_prompt [suffix] --- context."""
    parts = [p for p in (prefix, system_prompt, suffix) if p]
    parts.append("---")
    parts.append(context)
    return "\n\n".join(parts)


def handoff_prefix(from_agent: str, handoff_context: str) -> str:
    """A handoff banner so the next agent inherits the prior agent's context."""
    return (f"## Handoff from {from_agent}\n\n"
            f"The {from_agent} agent provided this context for you:\n\n"
            f"{handoff_context}\n\n---\n\nNow proceed with your role.")


def dispatch(name: str, context: str, *, prefix: str = "", suffix: str = "",
             cli: str = "claude", working_dir: Path | None = None,
             token_budget: int | None = None):
    """Load agent *name* and invoke it with *context*. Returns an AgentResponse."""
    from inertia_forge.agent import AgentResponse, AgentSession
    agent = load_agent_def(name)
    if agent is None:
        return AgentResponse(result="", is_error=True, error=f"no such agent: {name}")
    session = AgentSession(
        agent=cli, model=agent["model"], allowed_tools=agent["tools"] or None,
        permission_mode=agent["permission_mode"],
        working_dir=working_dir, token_budget=token_budget,
    )
    return session.invoke(build_agent_prompt(agent["system_prompt"], context, prefix, suffix))


def dispatch_with_handoff(name: str, context: str, from_agent: str,
                          handoff_context: str, **kw):
    """Dispatch *name* with a handoff banner from *from_agent*."""
    return dispatch(name, context, prefix=handoff_prefix(from_agent, handoff_context), **kw)


def run_dispatch(argv: list[str]) -> int:
    import argparse
    import json
    from inertia_forge.glyphs import seal
    p = argparse.ArgumentParser(prog="inertia-forge dispatch")
    p.add_argument("agent", help="agent name (.claude/agents/<name>.md)")
    p.add_argument("context", help="task context to send the agent")
    p.add_argument("--cli", default="claude", help="coding-agent CLI binary")
    p.add_argument("--budget", type=int, default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    resp = dispatch(args.agent, args.context, cli=args.cli, token_budget=args.budget)
    if args.json:
        print(json.dumps(resp.to_dict(), indent=2))
        return 1 if resp.is_error else 0
    if resp.is_error:
        print(f"{seal('error')} {resp.error}")
        return 1
    print(f"{seal('ok')} dispatched {args.agent}")
    print(resp.result)
    return 0
