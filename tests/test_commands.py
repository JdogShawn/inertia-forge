"""Tier 1 + Tier 2 commands: arch (AST rules), verify, skills validate,
state continuity, task budget, status."""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge import state as st, tasks as tk
from inertia_forge.cli import main
from inertia_forge.independent_analyzer import analyze_file
from inertia_forge.validate import validate_registry


def _rules(findings: list[dict]) -> set[str]:
    return {f["rule"] for f in findings}


class TestArchAstRules:
    def test_function_too_long(self, tmp_path: Path) -> None:
        body = "\n".join(f"    x{i} = {i}" for i in range(60))
        f = tmp_path / "big.py"
        f.write_text(f"def huge():\n{body}\n", encoding="utf-8")
        assert "function_too_long" in _rules(analyze_file(f))

    def test_too_many_functions(self, tmp_path: Path) -> None:
        f = tmp_path / "many.py"
        f.write_text("".join(f"def f{i}(): pass\n" for i in range(16)), encoding="utf-8")
        assert "too_many_functions" in _rules(analyze_file(f))

    def test_too_many_imports(self, tmp_path: Path) -> None:
        f = tmp_path / "imp.py"
        f.write_text("".join(f"import os as o{i}\n" for i in range(21)), encoding="utf-8")
        assert "too_many_imports" in _rules(analyze_file(f))

    def test_clean_file_passes(self, tmp_path: Path) -> None:
        f = tmp_path / "ok.py"
        f.write_text("import os\n\n\ndef f():\n    return os.getcwd()\n", encoding="utf-8")
        assert _rules(analyze_file(f)) == set()

    def test_syntax_error_degrades_gracefully(self, tmp_path: Path) -> None:
        f = tmp_path / "broken.py"
        f.write_text("def (:\n", encoding="utf-8")
        # AST rules return nothing on a syntax error; the call must not raise.
        analyze_file(f)


class TestArchCli:
    def test_arch_exit_1_on_p0(self, tmp_path: Path, capsys) -> None:
        f = tmp_path / "many.py"
        f.write_text("".join(f"def f{i}(): pass\n" for i in range(16)), encoding="utf-8")
        assert main(["arch", str(f)]) == 1

    def test_arch_exit_0_on_clean(self, tmp_path: Path) -> None:
        f = tmp_path / "ok.py"
        f.write_text("x = 1\n", encoding="utf-8")
        assert main(["arch", str(f)]) == 0


class TestSkillsValidate:
    def test_packaged_registry_is_valid(self) -> None:
        assert validate_registry() == []
        assert main(["skills", "validate"]) == 0

    def test_catches_bad_definition(self, tmp_path, monkeypatch) -> None:
        from inertia_forge import skill_registry as sr
        bad = tmp_path / "bad.yaml"
        bad.write_text(
            "broken:\n  evidence_mode: nonsense\n  steps: [a]\n"
            "  gates: {ghost: blocking}\n",  # gate on non-step + bad mode
            encoding="utf-8",
        )
        monkeypatch.setenv("INERTIA_FORGE_SKILLS", str(bad))
        sr._cache = None
        try:
            issues = validate_registry()
            assert any("unknown evidence_mode" in i for i in issues)
            assert any("unknown step" in i for i in issues)
        finally:
            sr._cache = None


class TestStateContinuity:
    def test_set_and_load(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        st.set_progress("did X", "do Y")
        data = st.load()
        assert data["last"] == "did X" and data["next"] == "do Y"
        assert data["history"][-1] == {"done": "did X", "next": "do Y"}

    def test_cli_roundtrip(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        assert main(["state", "--done", "shipped v1", "--next", "write docs"]) == 0
        assert st.load()["next"] == "write docs"


class TestVerify:
    def test_parse_passed_only(self) -> None:
        from inertia_forge.independent_analyzer import parse_pytest_summary
        assert parse_pytest_summary("==== 5 passed in 0.30s ====") == {
            "passed": 5, "failed": 0, "errors": 0, "coverage": None,
        }

    def test_parse_failed_and_coverage(self) -> None:
        from inertia_forge.independent_analyzer import parse_pytest_summary
        s = parse_pytest_summary("3 passed, 1 failed in 0.5s\nTOTAL  100  5  95%")
        assert s["passed"] == 3 and s["failed"] == 1 and s["coverage"] == 95

    def test_run_pytest_check_pass_then_fail(self, tmp_path: Path) -> None:
        from inertia_forge.independent_analyzer import run_pytest_check
        (tmp_path / "test_ok.py").write_text("def test_a():\n    assert True\n", encoding="utf-8")
        assert run_pytest_check(tmp_path) == []
        (tmp_path / "test_bad.py").write_text("def test_b():\n    assert False\n", encoding="utf-8")
        assert any(f["rule"] == "test_failure" for f in run_pytest_check(tmp_path))

    def test_verify_cli_reports_summary(self, tmp_path: Path, capsys) -> None:
        (tmp_path / "test_ok.py").write_text("def test_a():\n    assert True\n", encoding="utf-8")
        rc = main(["verify", str(tmp_path)])
        out = capsys.readouterr().out
        assert "VERIFY:" in out and "1 passed" in out
        assert rc == 0


class TestStateLog:
    def test_log_shows_history(self, tmp_path, monkeypatch, capsys) -> None:
        monkeypatch.chdir(tmp_path)
        st.set_progress("did a", "do b")
        assert main(["state", "--log"]) == 0
        assert "done: did a" in capsys.readouterr().out


class TestTaskBudgetAndStatus:
    def test_budget_and_status_run(self, tmp_path, monkeypatch, capsys) -> None:
        monkeypatch.chdir(tmp_path)
        tk.create_plan("feature", "Demo")
        tk.add_task("T1.1", "a", 8, ["x"], "pytest")
        tk.add_task("T1.2", "b", 12, ["y"], "pytest")
        assert main(["task", "budget"]) == 0
        assert "20" in capsys.readouterr().out          # total complexity 8+12
        assert main(["status"]) == 0
        assert "2 task" not in capsys.readouterr().err   # no crash
