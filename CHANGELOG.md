# Changelog

All notable changes to **inertia-forge**. This file is kept in step with the git
tags; regenerate the recent section any time with `inertia-forge changelog`.

The forge follows semantic-ish minor versions — each `0.N.0` adds a capability.

## 0.53.0
- `review-agent [diff|branch|commit]` — **agent-backed code review** (the forge's
  review intelligence). Dispatches focused reviewers over a diff — `nayru`
  (quality/correctness), `laverna` (security/OWASP), and `vaivora` (cross-module,
  added automatically for large diffs) — then classifies the combined findings
  into a verdict (request_changes / comment / approve) by P0/P1/P2 severity.
  The diff is fenced as untrusted data (prompt-injection guard); reviewers run
  read-only. The severity classification and size heuristic are pure
  deterministic logic (testable with no model via an injected dispatcher).
- `engage --review` now delegates its review judgment to this one review
  intelligence (diff-based, P0/P1/P2) instead of a separate verdict check — a
  single source of truth for "what a review is".

## 0.52.0
- `handoff pack <task-id>` / `handoff unpack <pkg>` — a **portable handoff
  package**. `pack` bundles a task (description, state, acceptance criteria), its
  relevant files (declared scope + recently changed), agent-specific
  instructions, and a token estimate into one `.tgz` (HANDOFF.md + metadata.json
  + context/); `unpack` extracts it and returns the metadata. Move a task to a
  different agent (codex, cursor, generic). Deterministic — tarball + JSON, no
  LLM. The bare `handoff` brief is unchanged.

## 0.51.0
- `dispatch <agent> <context>` — invoke a named agent from
  `.claude/agents/<name>.md` through the invoke bridge: load its model, tools,
  permission mode, and system prompt, prepend that prompt to the context, and
  run it via `AgentSession`. One agent can hand off to another with prior
  context (`dispatch_with_handoff`). The registry CRUD stays in `subagent`;
  this is the invocation layer. Still the one opt-in LLM bridge.

## 0.50.0
- `engage` gains depth on each task:
  - **Targeted tests** — maps the run's changed files to their conventional test
    paths (`git diff` → `tests/test_<mod>.py`) and tells the driver to run only
    those, not the whole suite. Deterministic; `--no-targeted-tests` opts out.
  - **Review-and-fix loop** (`--review`) — after a task is committed and
    verified, dispatch a reviewer; on a blocking verdict, dispatch a fixer and
    re-review up to `--max-review-iterations`. The loop and classification are
    deterministic; only the review/fix judgments use an agent. Off by default.
  - **Recovery guidance** — when the circuit breaker trips, name the dominant
    failure mode and the next concrete action instead of just "tripped".

## 0.49.0
- `engage` — the autonomous task-execution loop. Walks the task graph wave by
  wave (`taskgraph.parallel_waves` levels are the phases); for each pending task
  it skips when the acceptance criteria are already satisfied on disk, otherwise
  dispatches it, commits the result, verifies the commit carried meaningful
  output, and marks it done. A circuit breaker halts the run when the failure
  ratio crosses a threshold; a human-gated task (`requires: human`) pauses to
  resumable state under `.forge/engage/runs/`. `engage resume <run-id>` and
  `engage runs` manage paused runs.
- **Zero-LLM by construction:** `engage --dry-run` (or any injected task runner)
  drives the entire loop with no model calls. The agent dispatch reuses the
  `invoke` bridge; outcomes feed telemetry and the calibration loop.

## 0.48.0
- `invoke` — the one opt-in LLM bridge. Shell out to a coding-agent CLI
  (`claude -p … --output-format json`, or `codex exec`), parse
  result/cost/tokens/session, accumulate against a token budget, and record the
  call to telemetry. The deterministic core never calls it; `AgentSession`
  supports driver/navigator tool presets, permission modes, and session continue.
- `calibrate stats --type T [--family F]` — the full per-type record in one view:
  sample count, std_dev, p80, avg duration, success rate, MAPE, complexity/min,
  and recommended tier · model · effort. `record` now also takes `--outcome`
  and `--complexity`, which feed success rate and effort classification.

## 0.47.0
- `calibrate` gains per-type **std_dev** (population), `effort <complexity>`,
  `budget`, full **duration** estimate (avg + p80 minutes), and a `model`
  recommendation per type.
- `models` — **LLM-aware** model recommender (the forge recommends, never calls).
  Family-agnostic tiers (small/mid/frontier) with a current 2026 registry
  (anthropic/openai/codex/google/kimi/grok/deepseek/qwen/glm), overridable in
  `.forge/models.yaml`. Token + complexity drive the tier.

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
