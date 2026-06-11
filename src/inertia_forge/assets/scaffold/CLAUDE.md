# Project Instructions — enforced by INERTIA Forge

Work in this repo is mechanically enforced. The LLM adopts an **agent** role,
follows a **skill** methodology, and the **forge** gates the result — the session
closes only when every blocking gate is green. There is no escape hatch.

## The loop
1. **Plan** — `/forge-plan <goal>` (Vector) → a gated plan + well-formed tasks.
2. **Build** — `/forge-build` (Piston) → test-first; drive each task to green.
3. **Review** — `/forge-review` (Caliper) → measure the change against the spec.
4. **Ship** — `/forge-ship` → project gate (`inertia-forge check`) + PR.

Or start from a backlog: `/ignite <backlog.md>`.

## Non-negotiables
- **TDD** — a failing test before implementation, every time.
- `inertia-forge arch <changed files>` must be **0 P0** before a task is done.
- **No secrets, no gate bypass** — Bastion blocks dangerous ops; the forge logs
  every bypass attempt (`inertia-forge log`).
- Severity and test results are reported as observed — never softened, never
  claimed without running.

## Agents — `.claude/agents/`
Vector (plan) · Piston (build) · Caliper (review) · Bastion (security gate) ·
Sentinel (audit) · Gauge (QA) · Lattice (integration). Each keeps durable
lessons in `.claude/agent-memory/<agent>/MEMORY.md`.

## Quick reference
`inertia-forge status` · `arch` · `verify --cov` · `check` · `sweep` · `task` ·
`standup` · `doctor` · `contain`. Architecture limits: `.claude/rules/architecture.md`.
