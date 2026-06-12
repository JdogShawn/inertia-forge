"""v0.13.0 — INERTIA-branded visual system: palette, glyphs, brand, ui kit.

Deterministic: under pytest stdout is not a TTY, so colour is off by default and
paint() is a clean no-op — assertions read plain text. The colour path is
exercised by forcing FORCE_COLOR and resetting the detection caches.
"""
from __future__ import annotations

import pytest

from inertia_forge import brand, glyphs, palette, ui
from inertia_forge.cli import main


@pytest.fixture()
def color_on(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("FORCE_COLOR", "3")
    monkeypatch.setenv("COLORTERM", "truecolor")
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setattr(palette, "_TRUECOLOR", None)
    monkeypatch.setattr(palette, "_LIGHT", None)
    yield


class TestPalette:
    def test_paint_is_noop_without_color(self) -> None:
        # not a TTY under pytest -> no styling
        assert palette.paint("hello", "accent") == "hello"

    def test_paint_wraps_when_forced(self, color_on) -> None:
        out = palette.paint("hi", "accent", bold=True)
        assert out.startswith("\x1b[") and out.endswith(palette.RESET) and "hi" in out

    def test_strip_ansi(self) -> None:
        assert palette.strip_ansi("\x1b[38;2;0;255;209mX\x1b[0m") == "X"

    def test_no_color_env_disables(self, monkeypatch) -> None:
        monkeypatch.setenv("NO_COLOR", "1")
        assert palette.supports_color() is False

    def test_role_resolves_to_rgb(self) -> None:
        assert palette.rgb_for("success") == palette.PALETTE["cyan_dark"]


class TestGlyphs:
    def test_g_returns_renderable(self) -> None:
        assert glyphs.g("atom") in ("⚛", "*")
        assert glyphs.g("ok") in ("✓", "OK")

    def test_gate_badge_states(self) -> None:
        assert "CLEAR" in palette.strip_ansi(glyphs.gate_badge("open"))
        assert "SEALED" in palette.strip_ansi(glyphs.gate_badge("locked"))

    def test_seal_and_badge(self) -> None:
        assert palette.strip_ansi(glyphs.seal("error")) in ("✗", "XX")
        assert "READY" in palette.strip_ansi(glyphs.badge("READY"))


class TestBrand:
    def test_logo_variants(self) -> None:
        assert len(brand.logo("full")) == 14
        assert len(brand.logo("compact")) == 3
        assert len(brand.logo("tiny")) == 1

    def test_banner_carries_identity(self) -> None:
        plain = palette.strip_ansi(brand.banner(version="9.9.9"))
        assert "I N E R T I A" in plain and "F O R G E" in plain
        assert "v9.9.9" in plain and brand.VOW in plain

    def test_mini_header(self) -> None:
        assert "INERTIA FORGE" in palette.strip_ansi(brand.mini_header("1.2.3"))


class TestUiKit:
    def test_rule_plain(self) -> None:
        assert set(palette.strip_ansi(ui.rule(width=10))) <= {"─", "-"}

    def test_rule_with_label(self) -> None:
        assert "gates" in palette.strip_ansi(ui.rule("gates", width=40))

    def test_panel_frames_body(self) -> None:
        out = palette.strip_ansi(ui.panel("line one\nline two", title="box", width=40))
        assert "box" in out and "line one" in out and out.count("\n") >= 3

    def test_kv_aligns(self) -> None:
        out = palette.strip_ansi(ui.kv([("a", "1"), ("longkey", "2")]))
        assert "a" in out and "longkey" in out

    def test_progress_bar(self) -> None:
        assert "3/4" in palette.strip_ansi(ui.progress_bar(3, 4))

    def test_status_helpers_print(self, capsys) -> None:
        ui.ok("done"); ui.warn("hmm"); ui.err("nope"); ui.info("fyi")
        out = palette.strip_ansi(capsys.readouterr().out)
        assert "done" in out and "hmm" in out and "nope" in out and "fyi" in out


class TestCli:
    def test_banner_command(self, capsys) -> None:
        assert main(["banner"]) == 0
        assert "F O R G E" in palette.strip_ansi(capsys.readouterr().out)

    def test_logo_variants_command(self) -> None:
        assert main(["logo", "--variant", "tiny"]) == 0
        assert main(["logo", "--variant", "compact"]) == 0

    def test_status_renders_panel(self, capsys) -> None:
        assert main(["status"]) == 0
        assert "INERTIA FORGE" in palette.strip_ansi(capsys.readouterr().out)
