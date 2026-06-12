# Changelog

All notable changes to **inertia-forge**. This file is kept in step with the git
tags; regenerate the recent section any time with `inertia-forge changelog`.

The forge follows semantic-ish minor versions — each `0.N.0` adds a capability.

## 0.58.0
- **Per-task model routing** — `ignite run` routes the model by each task's
  complexity via a `routing:` section in `.forge/models.yaml` (tier → max
  complexity → model); no routing falls back to the fixed `--model`. Cheaper
  models for simple tasks, stronger ones for hard tasks.
- **Backlog dependency validation** — `backlog validate` / `ignite --check` now
  reject a **dependency cycle** and an **unknown dependency** (a `depends_on`
  pointing at a task id that isn't in the backlog), alongside the existing
  type/id/AC/verify/duplicate checks.
- **PR finalize parity** — `create_pr` auto-detects the base branch (requested
  base if it exists, else `dev`, else `main`), skips when an open PR already
  exists for the branch, and the body includes a **Blocked** section.

## 0.57.0
- **Dependency-blocked handling** — `ignite run` no longer dispatches a task
  whose dependency didn't complete: it records the dependent as `blocked`
  (reason `dependency_blocked`) and surfaces it. Blocked tasks count toward the
  circuit breaker. Closes a correctness gap vs the reference pipeline.
- **Protected-branch refusal** — `ignite run` refuses to run on `main`/`master`/
  `dev` (where it would commit straight to a protected branch); switch to a
  feature branch or pass `--force`. `--dry-run` is exempt. Safety gap closed.

## 0.56.0
- `ignite` ingest now reads **`depends_on:`** and **`requires:`** from a backlog,
  so a backlog drives the full pipeline: dependency-ordered waves (Kahn levels)
  and human-gated pauses (`requires: human`) are populated into the store at
  ingest — `ignite run` then executes in order and pauses at gated tasks.

## 0.55.0
- Naming consistency: the autonomous pipeline is named **ignite** throughout —
  the internal modules (`ignite_engine`, `ignite_runstate`, `ignite_commit`,
  `ignite_steps`, `ignite_review`, `ignite_recovery`, `ignite_targeted`,
  `ignite_predispatch`, `ignite_resume`), the classes (`IgniteConfig`,
  `IgniteRunner`, `IgniteResult`), the run-state path (`.forge/ignite/runs/`),
  and the commit prefix (`task(ignite):`). One name, end to end. No behavior change.

## 0.54.0
- **LLM-agnostic provider layer** (`providers`) — the agent bridge is no longer
  bound to one vendor. A provider is a command template + parse rule; a built-in
  registry ships adapters for claude · codex · gemini · cursor-agent · ollama ·
  llm, and `.forge/providers.yaml` adds or overrides any of them. `AgentSession`
  (and therefore *every* agent-backed capability — ignite, dispatch, review,
  security, planning) now runs on whatever LLM is configured.
- **`ignite` is the autonomous pipeline**, end to end and inertia-native with
  the bundled agents:
  - `ignite run` — walk the task graph wave by wave; **Piston** implements each
    task (gated, targeted tests, optional per-task review), then **finalize**:
    security-gate the branch with **Bastion** (fail-closed; a P0 blocks and
    withholds the PR) → review the branch with **Caliper/Sentinel/Lattice** →
    optional PR. Circuit breaker + recovery; human-gated pause/resume.
  - `ignite resume <id>` / `ignite runs` — manage paused runs.
  - `ignite plan "<goal>"` — **Vector** turns intent into a structured plan
    (summary · phases · files · complexity · risks).
  - `--dry-run` drives the whole loop with zero model calls.
- The autonomous pipeline lives entirely under `ignite` — one command, with the
  run/resume/runs/plan subcommands. The review agents are the forge's own
  (Caliper/Sentinel/Lattice), dispatched via their bundled definitions.

## 0.53.0
- `review-agent [diff|branch|commit]` — **agent-backed code review** (the forge's
  review intelligence). Dispatches the forge's review agents over a diff —
  `caliper` (quality/correctness), `sentinel` (security/OWASP), and `lattice`
  (cross-module, added automatically for large diffs) — then classifies findings
  into a verdict (request_changes / comment / approve) by P0/P1/P2 severity.
  The diff is fenced as untrusted data (prompt-injection guard); reviewers run
  read-only. The severity classification and size heuristic are pure
  deterministic logic (testable with no model via an injected dispatcher).
- `ignite --review` now delegates its review judgment to this one review
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
- `ignite` gains depth on each task:
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
- `ignite` — the autonomous task-execution loop. Walks the task graph wave by
  wave (`taskgraph.parallel_waves` levels are the phases); for each pending task
  it skips when the acceptance criteria are already satisfied on disk, otherwise
  dispatches it, commits the result, verifies the commit carried meaningful
  output, and marks it done. A circuit breaker halts the run when the failure
  ratio crosses a threshold; a human-gated task (`requires: human`) pauses to
  resumable state under `.forge/ignite/runs/`. `ignite resume <run-id>` and
  `ignite runs` manage paused runs.
- **Zero-LLM by construction:** `ignite --dry-run` (or any injected task runner)
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
