"""LLM provider adapters — the bridge that makes the forge work with ANY LLM.

The forge's agent capabilities (ignite, dispatch, review, security, planning) all
go through one bridge. That bridge is *not* bound to a single vendor: a provider
describes how to invoke a coding-agent CLI — its command template (with a
`{prompt}` / `{model}` placeholder), the flags for model / tools / permission /
session-continue, and how to read the result (`json` or plain `text`).

A built-in registry ships adapters for the common CLIs; `.forge/providers.yaml`
adds or overrides any of them, so a new LLM is a few lines of config, not code.
Pure data + string building — deterministic, no model is called here.
"""
from __future__ import annotations

import json
from pathlib import Path

CONFIG = Path(".forge") / "providers.yaml"

# name -> adapter spec. `parse: json` expects a structured result with usage;
# `parse: text` treats stdout as the whole answer (the common case for CLIs that
# just print). Flags are only appended when the spec defines them.
_DEFAULT_PROVIDERS: dict[str, dict] = {
    "claude": {
        "command": ["claude", "-p", "{prompt}", "--output-format", "json"],
        "model_flag": "--model", "tools_flag": "--allowedTools",
        "permission_flag": "--permission-mode", "continue_flag": "--continue",
        "parse": "json",
    },
    "codex": {"command": ["codex", "exec", "{prompt}"], "model_flag": "--model",
              "parse": "text"},
    "gemini": {"command": ["gemini", "-p", "{prompt}"], "model_flag": "--model",
               "parse": "text"},
    "cursor-agent": {"command": ["cursor-agent", "-p", "{prompt}"],
                     "model_flag": "--model", "parse": "text"},
    "ollama": {"command": ["ollama", "run", "{model}", "{prompt}"], "parse": "text"},
    "llm": {"command": ["llm", "-m", "{model}", "{prompt}"], "parse": "text"},
}


def providers() -> dict[str, dict]:
    """The provider registry — built-in defaults merged with `.forge/providers.yaml`."""
    out = {k: dict(v) for k, v in _DEFAULT_PROVIDERS.items()}
    if CONFIG.exists():
        import yaml
        try:
            data = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            data = {}
        for name, spec in data.items():
            if isinstance(spec, dict):
                out[name] = {**out.get(name, {}), **spec}
    return out


def get(name: str) -> dict:
    """The adapter for *name*, falling back to the claude adapter shape."""
    return providers().get(name, _DEFAULT_PROVIDERS["claude"])


def build_command(name: str, prompt: str, *, model: str | None = None,
                  tools: list[str] | None = None, permission_mode: str = "auto",
                  session_id: str | None = None, cont: bool = False) -> list[str]:
    """Render a provider's argv for *prompt* (deterministic, no shell)."""
    spec = get(name)
    argv = [tok.replace("{prompt}", prompt).replace("{model}", model or "")
            for tok in spec.get("command", [])]
    if model and spec.get("model_flag"):
        argv += [spec["model_flag"], model]
    if tools and spec.get("tools_flag"):
        argv += [spec["tools_flag"], ",".join(tools)]
    elif permission_mode != "auto" and spec.get("permission_flag"):
        argv += [spec["permission_flag"], permission_mode]
    if cont and session_id and spec.get("continue_flag"):
        argv += [spec["continue_flag"], session_id]
    return argv


def parse(name: str, stdout: str) -> dict:
    """Normalize provider stdout to {result, session_id, tokens, cost, model, error}."""
    blank = {"result": "", "session_id": None, "input_tokens": 0, "output_tokens": 0,
             "cost_usd": 0.0, "model": "unknown", "is_error": False, "error": None}
    if get(name).get("parse") == "text":
        return {**blank, "result": stdout}
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return {**blank, "result": stdout}  # CLI printed plain text despite json mode
    usage = data.get("usage", {})
    return {
        "result": data.get("result", ""), "session_id": data.get("session_id"),
        "input_tokens": int(usage.get("input_tokens", 0)),
        "output_tokens": int(usage.get("output_tokens", 0)),
        "cost_usd": float(data.get("total_cost_usd", 0.0)),
        "model": next(iter(data.get("modelUsage", {})), "unknown"),
        "is_error": bool(data.get("is_error", False)),
        "error": data.get("error") if data.get("is_error") else None,
    }


def run_providers(argv: list[str]) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="inertia-forge providers")
    sub = p.add_subparsers(dest="sub")
    sub.add_parser("list")
    sh = sub.add_parser("show")
    sh.add_argument("name")
    args = p.parse_args(argv)
    reg = providers()
    if args.sub == "show":
        spec = reg.get(args.name)
        if not spec:
            print(f"no such provider: {args.name}")
            return 1
        print(f"{args.name}: {' '.join(spec.get('command', []))} [{spec.get('parse', 'json')}]")
        return 0
    for name in sorted(reg):
        spec = reg[name]
        print(f"  {name:14} {spec.get('parse', 'json'):5} {' '.join(spec.get('command', []))}")
    print(f"\noverride or add in {CONFIG}")
    return 0
