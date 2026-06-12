# Changelog

All notable changes to **inertia-forge**. This file is kept in step with the git
tags; regenerate the recent section any time with `inertia-forge changelog`.

The forge follows semantic-ish minor versions — each `0.N.0` adds a capability.

## 0.45.0
- `report` — one markdown health page unifying the scan battery, code-quality
  metrics, and task progress (CI artifact / LLM-friendly).

## 0.44.0
- `release checklist` is now a real readiness gate (versions · clean tree ·
  CHANGELOG entry · tests collectable · doc freshness), not a static list.

## 0.43.0
- `mermaid` — export the task DAG and module import graph as Mermaid diagrams.

## 0.42.0
- `policy` — configurable banned-call lint (`.forge/banned.txt`, `# noqa: policy`).

## 0.41.0
- `verify-output` — flag empty / metadata-only work (no real code changed).

## 0.40.0
- `calibrate` — per-type baselines + forward estimation (mean + p80).

## 0.39.0
- `suggest-split` — threshold-gated, class-aware module-split adviser.

## 0.38.0
- `scan` — the full quality battery in one verdict; MCP expanded to 28 tools;
  `review` self-flag fixed.

## 0.30.0 – 0.37.0
- SQLite telemetry store, signals + outcomes, semantic memory, the task-
  intelligence layer, QC schema parity, cross-reference integrity (`xref`),
  flaky + broken-export detection, calibration + query, dead-code, complexity,
  imports, docs/types coverage, changelog, coverage gate, the gated tool set.

## 0.1.0 – 0.29.0
- The deterministic enforcement core: forge sessions + blocking gates, the
  native task store, arch/check/sweep/vet, the INERTIA visual system, the
  statusline, agents + skills, hooks, MCP server, and the analysis suite.
  See the git tags for the full per-version history.
