"""v0.7.0 — bundled INERTIA agents + skill docs, ignite rename, secret scanner."""
from __future__ import annotations

from pathlib import Path

import pytest

from inertia_forge.cli import main


@pytest.fixture()
def proj(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".forge").mkdir()
    return tmp_path


class TestAssets:
    def test_roster_and_skill_docs_present(self) -> None:
        from inertia_forge import assets
        roster = assets.agent_names()
        assert set(roster) == {"vector", "piston", "caliper", "bastion",
                               "sentinel", "gauge", "lattice"}
        assert "implementing-with-tdd" in assets.skill_names()

    def test_install(self, proj: Path) -> None:
        from inertia_forge import assets
        agents = assets.install_agents(proj)
        skills = assets.install_skills(proj)
        assert (proj / ".claude" / "agents" / "piston.md").exists()
        assert (proj / ".claude" / "skills" / "implementing-with-tdd" / "SKILL.md").exists()
        assert len(agents) == 7 and len(skills) >= 8

    def test_cli_list_and_show(self, proj: Path, capsys) -> None:
        assert main(["agents"]) == 0
        assert "piston" in capsys.readouterr().out
        assert main(["agents", "show", "vector"]) == 0
        assert "Vector" in capsys.readouterr().out


class TestSkillDocsWired:
    def test_doc_paths_resolve_after_install(self, proj: Path) -> None:
        from inertia_forge import assets
        from inertia_forge.skill_registry import get_skill
        assert get_skill("implementing_with_tdd").doc == ".claude/skills/implementing-with-tdd/SKILL.md"
        assets.install_skills(proj)
        # `read` verifies the doc exists, then marks it read.
        assert main(["read", "implementing_with_tdd"]) == 0


class TestIgniteEnriched:
    def test_sets_next_and_suggests_agent(self, proj: Path, capsys) -> None:
        b = proj / "b.md"
        b.write_text("# Login\ntype: feature\n\n## T1.1: build login\ncomplexity: 5\n"
                     "- [ ] works\nverify: pytest\n", encoding="utf-8")
        assert main(["ignite", str(b)]) == 0
        out = capsys.readouterr().out
        assert "IGNITED" in out and "agent:" in out
        from inertia_forge import state as st
        assert "build login" in st.load()["next"]


class TestSecretScanner:
    @pytest.mark.parametrize("secret", [
        "pypi-AAAAAAAAAAAAAAAAAAAAAA",
        "ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        'token = "supersecretvalue123"',
    ])
    def test_catches_modern_tokens(self, proj: Path, secret: str) -> None:
        f = proj / "leak.txt"
        f.write_text(secret + "\n", encoding="utf-8")
        from inertia_forge.commands import _scan_secrets
        assert any(x["rule"] == "possible_secret" for x in _scan_secrets(f))
