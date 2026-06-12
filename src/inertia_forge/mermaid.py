"""Mermaid export — render the forge's graphs as Mermaid diagrams.

Turns the deterministic graphs into Mermaid flowcharts an LLM or a markdown
viewer can render directly: ``mermaid tasks`` draws the task dependency DAG
(done/ready nodes shaded in the brand palette), ``mermaid imports [path]`` draws
the module import graph. Pure text — paste into any Mermaid renderer or a
markdown doc. Deterministic.
"""
from __future__ import annotations

import argparse
import re


def _nid(name: str) -> str:
    """A Mermaid-safe node id."""
    return re.sub(r"[^0-9a-zA-Z]", "_", name)


def tasks_mermaid() -> str:
    from inertia_forge import tasks as t, taskgraph as tg
    tasks = t.list_tasks()
    ready = {x["id"] for x in tg.ready_tasks()}
    lines = ["flowchart TD"]
    for x in tasks:
        nid = _nid(x["id"])
        lines.append(f'    {nid}["{x["id"]}: {x["title"][:28]}"]')
        if x["status"] == "done":
            lines.append(f"    class {nid} done")
        elif x["id"] in ready:
            lines.append(f"    class {nid} ready")
    for x in tasks:
        for dep in x.get("depends_on", []):
            lines.append(f"    {_nid(dep)} --> {_nid(x['id'])}")
    lines += ["    classDef done fill:#00C9A7,color:#000",
              "    classDef ready fill:#00FFD1,color:#000"]
    return "\n".join(lines)


def imports_mermaid(path: str) -> str:
    from inertia_forge.importgraph import _find_package, build_graph
    graph = build_graph(_find_package(path))
    lines = ["flowchart LR"]
    for mod, deps in sorted(graph.items()):
        for dep in sorted(deps):
            lines.append(f"    {_nid(mod.split('.')[-1])} --> {_nid(dep.split('.')[-1])}")
    return "\n".join(lines)


def run_mermaid(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="inertia-forge mermaid")
    sub = p.add_subparsers(dest="sub", required=True)
    sub.add_parser("tasks", help="task dependency DAG")
    im = sub.add_parser("imports", help="module import graph")
    im.add_argument("path", nargs="?", default=".")
    args = p.parse_args(argv)
    print(tasks_mermaid() if args.sub == "tasks" else imports_mermaid(args.path))
    return 0
