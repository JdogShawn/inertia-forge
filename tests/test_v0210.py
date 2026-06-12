"""v0.21.0 — insecure-code vetting (bandit-lite, AST-based). Hermetic: planted
patterns parsed directly, no external tools.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import vet
from inertia_forge.cli import main


def _vet(tmp: Path, src: str) -> list[dict]:
    f = tmp / "m.py"
    f.write_text(src, encoding="utf-8")
    return vet.vet_file(f)


class TestVet:
    def test_eval_and_exec_are_p1(self, tmp_path: Path) -> None:
        sev = [x["severity"] for x in _vet(tmp_path, "eval(x)\nexec(y)\n")]
        assert sev == ["P1", "P1"]

    def test_shell_true_is_p1(self, tmp_path: Path) -> None:
        out = _vet(tmp_path, "import subprocess\nsubprocess.run('ls', shell=True)\n")
        assert out and out[0]["severity"] == "P1" and "shell=True" in out[0]["message"]

    def test_shell_false_not_flagged(self, tmp_path: Path) -> None:
        assert _vet(tmp_path, "import subprocess\nsubprocess.run(['ls'], shell=False)\n") == []

    def test_advisory_p2_set(self, tmp_path: Path) -> None:
        src = ("import os, pickle, yaml, hashlib\n"
               "os.system('x')\npickle.loads(b'')\nyaml.load('a')\nhashlib.md5(b'')\n")
        msgs = " ".join(x["message"] for x in _vet(tmp_path, src))
        assert all(s in msgs for s in ("os.system", "pickle.loads", "yaml.load", "hashlib.md5"))
        assert all(x["severity"] == "P2" for x in _vet(tmp_path, src))

    def test_yaml_load_with_loader_ok(self, tmp_path: Path) -> None:
        assert _vet(tmp_path, "import yaml\nyaml.load('a', Loader=yaml.SafeLoader)\n") == []

    def test_sql_fstring_is_p1(self, tmp_path: Path) -> None:
        out = _vet(tmp_path, "q = f\"SELECT * FROM t WHERE id={uid}\"\n")
        assert out and out[0]["severity"] == "P1" and "SQL" in out[0]["message"]

    def test_string_mention_not_flagged(self, tmp_path: Path) -> None:
        # 'eval' in a string/comment must NOT trip the AST check
        assert _vet(tmp_path, "msg = 'do not eval untrusted input'  # exec is bad\n") == []

    def test_non_python_skipped(self, tmp_path: Path) -> None:
        f = tmp_path / "x.js"
        f.write_text("eval(x)\n", encoding="utf-8")
        assert vet.vet_file(f) == []

    def test_cli_exit_codes(self, tmp_path: Path, monkeypatch) -> None:
        (tmp_path / "bad.py").write_text("eval(x)\n", encoding="utf-8")
        (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        assert main(["vet", "bad.py"]) == 1
        assert main(["vet", "ok.py"]) == 0
