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


def _props(**kw: str) -> dict:
    return {"type": "object",
            "properties": {k: {**_STR, "description": v} for k, v in kw.items()},
            "required": list(kw)}


def _p(a: dict) -> str:
    return a.get("path", ".")


# name -> (description, inputSchema, argv-builder)
_TOOLS = [
    # ── read / state ────────────────────────────────────────────────
    ("forge_status", "Active forge session + plan/tasks + last/next", {"type": "object"},
     lambda a: ["status"]),
    ("forge_json", "Machine-readable state (status/tasks/graph/plan/consistency/freshness/budget)",
     _props(query="one of: status, tasks, graph, plan, consistency, freshness, budget"),
     lambda a: ["json", a.get("query", "status")]),
    ("forge_tasks", "List the native task store", {"type": "object"}, lambda a: ["task", "list"]),
    ("forge_skills", "List the registered skills + evidence modes", {"type": "object"},
     lambda a: ["skills"]),
    ("forge_doctor", "Health check of the forge setup", {"type": "object"}, lambda a: ["doctor"]),
    # ── analysis / gates (read-only) ────────────────────────────────
    ("forge_arch", "Architecture check (size/structure)", _path_schema("file/dir"),
     lambda a: ["arch", _p(a)]),
    ("forge_check", "Project gate: arch + secrets", _path_schema("project path"),
     lambda a: ["check", _p(a)]),
    ("forge_sweep", "Find unused imports", _path_schema("file/dir"), lambda a: ["sweep", _p(a)]),
    ("forge_review", "Review smells: debug leftovers, markers, endpoints", _path_schema("file/dir"),
     lambda a: ["review", _p(a)]),
    ("forge_vet", "Insecure-code scan (eval/exec/shell=True/pickle/...)", _path_schema("file/dir"),
     lambda a: ["vet", _p(a)]),
    ("forge_complexity", "Cyclomatic complexity per function", _path_schema("file/dir"),
     lambda a: ["complexity", _p(a)]),
    ("forge_imports", "Module import graph + circular-import detection", _path_schema("project/pkg"),
     lambda a: ["imports", _p(a)]),
    ("forge_dead_code", "Defined-but-never-referenced symbols", _path_schema("project/pkg"),
     lambda a: ["dead-code", _p(a)]),
    ("forge_docs", "Docstring coverage of the public surface", _path_schema("file/dir"),
     lambda a: ["docs", _p(a)]),
    ("forge_types", "Type-hint coverage", _path_schema("file/dir"), lambda a: ["types", _p(a)]),
    ("forge_qc", "Run a declarative QC suite (.qc.yaml)", _props(suite="path to a .qc.yaml"),
     lambda a: ["qc", a.get("suite", "")]),
    # ── gated tools (enforced execution / file ops) ─────────────────
    ("forge_run", "GATED command execution — blocked refused, review refused (safe)",
     _props(command="the command to run"), lambda a: ["run", *a.get("command", "").split()]),
    ("forge_write", "GATED write — containment-tier checked",
     _props(path="file path", content="content to write"),
     lambda a: ["write", a.get("path", ""), "--content", a.get("content", "")]),
    ("forge_edit", "GATED edit — exact unique-match replacement, containment-checked",
     _props(path="file path", old="exact text to replace", new="replacement"),
     lambda a: ["edit", a.get("path", ""), "--old", a.get("old", ""), "--new", a.get("new", "")]),
    ("forge_view", "GATED read — blocked paths refused", _path_schema("file path"),
     lambda a: ["view", _p(a)]),
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
