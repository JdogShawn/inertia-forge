"""v0.42.0 — policy lint: flag project-banned function calls (configurable),
with a # noqa: policy escape. Generalizes a raw-subprocess lint rule.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from inertia_forge import policy
from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


def _ban(proj: Path, text: str) -> None:
    (proj / ".forge" / "banned.txt").write_text(text, encoding="utf-8")


class TestPolicy:
    def test_load_banned_parses_reasons(self, proj: Path) -> None:
        _ban(proj, "subprocess.run  # use a wrapper\nprint\n# a comment line\n")
        b = policy.load_banned()
        assert b == {"subprocess.run": "use a wrapper", "print": ""}

    def test_call_name(self) -> None:
        def cn(src: str) -> str:
            return policy._call_name(ast.parse(src).body[0].value)
        assert cn("subprocess.run(x)") == "subprocess.run"
        assert cn("print(x)") == "print"
        assert cn("a.b.c(x)") == "a.b.c"

    def test_scan_dotted_and_noqa(self, proj: Path) -> None:
        f = proj / "m.py"
        f.write_text("import subprocess\ndef g():\n    subprocess.run([])\n"
                     "    print('x')  # noqa: policy\n", encoding="utf-8")
        names = [h[2] for h in policy.scan_file(f, {"subprocess.run": "", "print": ""})]
        assert "subprocess.run" in names and "print" not in names  # print is noqa'd

    def test_bare_name_match(self, proj: Path) -> None:
        f = proj / "m.py"
        f.write_text("def g():\n    print('x')\n", encoding="utf-8")
        assert policy.scan_file(f, {"print": ""})  # bare callee matches

    def test_not_a_call_not_flagged(self, proj: Path) -> None:
        f = proj / "m.py"
        f.write_text("def g():\n    ref = print\n    return ref\n", encoding="utf-8")
        assert policy.scan_file(f, {"print": ""}) == []  # assignment, not a call


class TestCli:
    def test_no_config_clean(self, proj: Path) -> None:
        assert main(["policy", "."]) == 0

    def test_flags_banned(self, proj: Path) -> None:
        _ban(proj, "eval  # no dynamic eval\n")
        (proj / "v.py").write_text("eval('x')\n", encoding="utf-8")
        assert main(["policy", "v.py"]) == 1

    def test_clean_file_passes(self, proj: Path) -> None:
        _ban(proj, "eval\n")
        (proj / "clean.py").write_text("x = 1\n", encoding="utf-8")
        assert main(["policy", "clean.py"]) == 0
