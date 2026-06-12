"""LLM-aware model recommender — pick the right model *tier* for the work.

The forge never CALLS a model (the no-LLM moat holds) — it only RECOMMENDS one,
deterministically, from a task's calibrated token/complexity profile. The
recommendation is model-family-agnostic: it picks a tier (small / mid / frontier)
and maps it to a model in your chosen family (anthropic, openai, google, kimi,
grok, deepseek, qwen, glm). Ships current 2026 defaults; override or add any
family in ``.forge/models.yaml``.

Tier thresholds (token-driven, the calibration-engine convention): avg tokens
< 20K → small (docs/fixes), < 60K → mid (standard features), otherwise frontier
(hard refactors). A high task-complexity score bumps the tier up.
"""
from __future__ import annotations

from pathlib import Path

SMALL_TOKENS = 20_000
MID_TOKENS = 60_000
_TIERS = ("small", "mid", "frontier")
CONFIG = Path(".forge") / "models.yaml"

# 2026 defaults: small = cheap/fast, mid = daily driver, frontier = the hard 20%.
_DEFAULT_FAMILIES: dict[str, dict[str, str]] = {
    "anthropic": {"small": "claude-haiku-4-5", "mid": "claude-sonnet-4-6", "frontier": "claude-opus-4-8"},
    "openai": {"small": "gpt-5.4-mini", "mid": "gpt-5.4", "frontier": "gpt-5.5"},
    "google": {"small": "gemini-3-flash", "mid": "gemini-3-pro", "frontier": "gemini-3.1-pro"},
    "kimi": {"small": "kimi-k2-flash", "mid": "kimi-k2.6", "frontier": "kimi-k2.6"},
    "grok": {"small": "grok-4-mini", "mid": "grok-4.3", "frontier": "grok-4.3"},
    "deepseek": {"small": "deepseek-v4-flash", "mid": "deepseek-v4", "frontier": "deepseek-v4-pro-max"},
    "qwen": {"small": "qwen3-coder-flash", "mid": "qwen3-coder", "frontier": "qwen3.7-max"},
    "glm": {"small": "glm-5-air", "mid": "glm-5", "frontier": "glm-5"},
    "codex": {"small": "gpt-5.4-codex-mini", "mid": "gpt-5.4-codex", "frontier": "gpt-5.5-codex"},
    "tier": {"small": "small", "mid": "mid", "frontier": "frontier"},
}


def families() -> dict[str, dict[str, str]]:
    """The model registry — 2026 defaults merged with any .forge/models.yaml override."""
    fams = {k: dict(v) for k, v in _DEFAULT_FAMILIES.items()}
    if CONFIG.exists():
        import yaml
        try:
            user = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
            for fam, tiers in user.items():
                if isinstance(tiers, dict):
                    fams.setdefault(fam, {}).update(tiers)
        except yaml.YAMLError:
            pass
    return fams


def recommend_tier(avg_tokens: float, complexity: float | None = None) -> str:
    """Tier from avg tokens (and complexity, which can only bump it up)."""
    tier = "small" if avg_tokens < SMALL_TOKENS else ("mid" if avg_tokens < MID_TOKENS else "frontier")
    if complexity is not None:
        ctier = "small" if complexity < 20 else ("mid" if complexity <= 60 else "frontier")
        tier = max(tier, ctier, key=_TIERS.index)
    return tier


def recommend_model(avg_tokens: float, family: str = "anthropic",
                    complexity: float | None = None) -> tuple[str, str]:
    """(tier, model_name) for *family*. Unknown family → the agnostic tier name."""
    tier = recommend_tier(avg_tokens, complexity)
    fam = families().get(family, _DEFAULT_FAMILIES["tier"])
    return tier, fam.get(tier, tier)


def run_models(argv: list[str]) -> int:
    import argparse
    from inertia_forge.glyphs import g, seal
    from inertia_forge.palette import paint
    p = argparse.ArgumentParser(prog="inertia-forge models")
    sub = p.add_subparsers(dest="sub", required=True)
    sub.add_parser("list", help="show the model registry")
    rec = sub.add_parser("recommend", help="recommend a model for a token/complexity profile")
    rec.add_argument("--tokens", type=float, required=True)
    rec.add_argument("--family", default="anthropic")
    rec.add_argument("--complexity", type=float, default=None)
    args = p.parse_args(argv)
    if args.sub == "list":
        for fam, tiers in sorted(families().items()):
            row = " ".join(f"{paint(tier, 'muted')}:{tiers[tier]}" for tier in _TIERS if tier in tiers)
            print(f"  {paint(fam.ljust(10), 'accent')} {row}")
        return 0
    tier, model = recommend_model(args.tokens, args.family, args.complexity)
    print(f"{seal('ok')} {args.family} {g('arrow_r')} {paint(tier, 'accent', bold=True)} "
          f"{g('dot')} {paint(model, 'success', bold=True)}")
    return 0
