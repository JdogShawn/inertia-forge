"""ignite ingest wires depends_on + requires:human from the backlog."""
from pathlib import Path
import pytest
from inertia_forge import tasks, taskgraph
from inertia_forge.ignite import parse_backlog, run_ignite

@pytest.fixture()
def proj(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path); (tmp_path/".forge").mkdir(); return tmp_path

def test_parse_captures_deps_and_requires():
    _, ts = parse_backlog("## T1.1: a\nverify: pytest\n- [ ] x\n\n"
                          "## T1.2: b\ndepends_on: T1.1\nrequires: human\nverify: pytest\n- [ ] y\n")
    assert ts[1]["depends_on"] == ["T1.1"] and ts[1]["requires"] == "human"

def test_ingest_wires_graph_and_gate(proj):
    bl = proj/"b.md"
    bl.write_text("# P\ntype: feature\n## T1.1: a\nverify: pytest\n- [ ] x\n\n"
                  "## T1.2: b\ndepends_on: T1.1\nrequires: human\nverify: pytest\n- [ ] y\n", encoding="utf-8")
    run_ignite([str(bl)])
    assert tasks.get_task("T1.2")["depends_on"] == ["T1.1"]
    assert tasks.get_task("T1.2")["requires"] == "human"
    # dependency wave order honored
    assert taskgraph.parallel_waves() == [["T1.1"], ["T1.2"]]
