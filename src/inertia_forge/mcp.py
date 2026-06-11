"""MCP server — expose the forge's deterministic commands as MCP tools.

`inertia-forge mcp serve` speaks JSON-RPC 2.0 over stdio (newline-delimited),
so any MCP client (e.g. Claude) can call the forge's tools. The server itself
is pure and deterministic — the LLM is the *client*; the forge tools it calls
never invoke a model. No external SDK: the protocol is implemented directly.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys

_STR = {"type": "string"}


def _path_schema(desc: str) -> dict:
    return {"type": "object", "properties": {"path": {**_STR, "description": desc}}}


# name -> (description, inputSchema, argv-builder)
_TOOLS = [
    ("forge_status", "Active forge session + plan/tasks + last/next", {"type": "object"},
     lambda a: ["status"]),
    ("forge_arch", "Deterministic architecture check of a path", _path_schema("file/dir"),
     lambda a: ["arch", a.get("path", ".")]),
    ("forge_check", "Project gate: arch + secrets on a path", _path_schema("project path"),
     lambda a: ["check", a.get("path", ".")]),
    ("forge_sweep", "Find unused imports in a path", _path_schema("file/dir"),
     lambda a: ["sweep", a.get("path", ".")]),
    ("forge_skills", "List the registered skills + evidence modes", {"type": "object"},
     lambda a: ["skills"]),
    ("forge_tasks", "List the native task store", {"type": "object"},
     lambda a: ["task", "list"]),
    ("forge_doctor", "Health check of the forge setup", {"type": "object"},
     lambda a: ["doctor"]),
]


def _run_tool(name: str, arguments: dict) -> str:
    from inertia_forge.cli import main
    spec = next((t for t in _TOOLS if t[0] == name), None)
    if spec is None:
        return f"unknown tool: {name}"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        with contextlib.suppress(SystemExit):
            main(spec[3](arguments or {}))
    return buf.getvalue() or "(no output)"


def _result(rid, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": rid, "result": result}


def handle(req: dict) -> dict | None:
    """Return a JSON-RPC response, or None for notifications."""
    from inertia_forge import __version__
    method, rid = req.get("method"), req.get("id")
    if method == "initialize":
        return _result(rid, {"protocolVersion": "2024-11-05",
                             "capabilities": {"tools": {}},
                             "serverInfo": {"name": "inertia-forge", "version": __version__}})
    if method == "tools/list":
        return _result(rid, {"tools": [{"name": n, "description": d, "inputSchema": s}
                                       for n, d, s, _ in _TOOLS]})
    if method == "tools/call":
        params = req.get("params", {})
        text = _run_tool(params.get("name", ""), params.get("arguments") or {})
        return _result(rid, {"content": [{"type": "text", "text": text}], "isError": False})
    if method and method.startswith("notifications/"):
        return None
    if rid is not None:
        return {"jsonrpc": "2.0", "id": rid,
                "error": {"code": -32601, "message": f"method not found: {method}"}}
    return None


def serve() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
    return 0


def run_mcp(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge mcp")
    sub = p.add_subparsers(dest="sub", required=True)
    sub.add_parser("serve", help="run the stdio MCP server")
    sub.add_parser("tools", help="list exposed MCP tools")
    args = p.parse_args(argv)
    if args.sub == "tools":
        for n, d, _s, _b in _TOOLS:
            print(f"  {n:16} {d}")
        return 0
    return serve()
