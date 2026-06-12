# INERTIA Forge — 慣性

**A project-agnostic, deterministic skill-enforcement engine. The only way out is to do the work.**

> *Newton's first law for code quality:* work at rest stays at rest, work in motion must clear every gate. That's **inertia** — and it's the law this forge enforces.

INERTIA Forge is the deterministic enforcement core of the **INERTIA** cognition platform, extracted to stand alone. It is **its own tool**, not a wrapper around any other — it ships its own task store, its own analyzer, its own continuity, audit, and containment. It needs nothing but Python.

The forge makes a skill's methodology *mechanically enforced*. Invoking a skill opens a **session** with **blocking gates**. You can't manually close it, you can't skip a gate, and you can't fake evidence — the session auto-closes only when the last blocking gate is recorded with a real, hash-verified result. No escape hatch by design.

**Zero LLM calls. Pure deterministic algorithms.** Every gate decision is explainable and reproducible — same inputs, same verdict, every time.

---

## Install

```bash
pip install inertia-forge
```

## Quick start (programmatic)

```python
from pathlib import Path
from inertia_forge import ForgeSkillBridge, get_required_steps

bridge = ForgeSkillBridge("reviewing_code", "src/", claude_session_id="my-tab")
bridge.start_session()                         # 2 blocking gates open
for phase in get_required_steps("reviewing_code"):
    bridge.record_phase(phase, Path("src"))     # auto-closes on the last green gate
```

## Quick start (CLI)

```bash
inertia-forge skills                       # list registered skills + modes
inertia-forge start reviewing_code src/    # open a session
inertia-forge record-phase check_correctness src/
inertia-forge status
# `close` is intentionally refused while gates remain — record them instead.
```

## Commands

| command | what it does |
|---|---|
| `inertia-forge skills` / `validate` / `export` / `new` / `score` / `search <query>` | list / validate / export / scaffold / score / **recommend** skills |
| `inertia-forge doctor [--fix]` | health check of the forge setup (python, pytest, .forge, registry, hooks) |
| `inertia-forge start <skill> <target>` | open a forge session |
| `inertia-forge record-phase <phase> <target>` | record a phase (auto-closes on all-green) |
| `inertia-forge status` | forge session + plan + task progress + last/next |
| `inertia-forge arch <path>…` | deterministic architecture check (file size, **function length, functions/file, imports/file**, stubs, broad-except, …) — exits 1 on any P0 |
| `inertia-forge verify [dir] [--cov PKG]` | run pytest + report pass/fail/coverage |
| `inertia-forge check [path] [--tests DIR] [--deps]` | **project gate** — arch + secrets (+ tests + dep audit) as one pass/fail (pre-commit/CI) |
| `inertia-forge sweep [path] [--fix]` | find (or remove) unused imports |
| `inertia-forge scan-deps [path]` | dependency vulnerability scan (pip-audit, optional) |
| `inertia-forge task …` | native task store: `plan`/`add [--depends-on]`/`start`/`ac`/`ac-add`/`set`/`done`/`list`/`show`/`budget [--max]`/`next`/`archive`/`restore`/`list-archived`/`cleanup`/`changelog` |
| `inertia-forge task deps/ready/graph/estimate/audit` | dependency graph: set deps, list ready (deps-met) tasks, show parallel waves + cycles, heuristic complexity estimate, store-consistency audit |
| `inertia-forge consistency` | task-store invariants (done-with-unmet-AC, dangling/self deps, cycles) — exits 1 on drift |
| `inertia-forge role <path>…` | classify files by role (test/cli/config/doc/data/source) |
| `inertia-forge targeted [--since REF] [files…]` | map changed sources → the test files that cover them (run only what a change can break) |
| `inertia-forge preset list/show/apply <name>` | named config archetypes (library/service/cli/data) |
| `inertia-forge verify-commit [--require-task]` | post-commit gate: clean tree (churn-filtered) + HEAD references a task id |
| `inertia-forge scope set <id> --paths …` / `scope check` | declare a task's path scope; flag working-tree changes outside the active task's scope |
| `inertia-forge freshness [--days N]` | flag stale/missing continuity files (CLAUDE.md, context docs, state) |
| `inertia-forge tokens <path>… [--glob G] [--quiet]` | deterministic token estimate for a file/tree (no tokenizer dep) |
| `inertia-forge backlog validate <file>` | validate a backlog .md (plan type, task ids, AC, verify) before ingest; `ignite --check` pre-flights |
| `inertia-forge plan estimate [--tokens-per-point N] [--threshold T]` | project a session-token cost from remaining complexity; exits 1 if over threshold |
| `inertia-forge handoff [--write]` | structured end-of-session brief: active task, ready/blocked waves, recent commits, continuity, drift |
| `inertia-forge prune [--keep N] [--days D]` | bound runtime growth — trim the behavioral log + age out cache blobs |
| `inertia-forge json <query>` | machine-readable state for agents (`status`/`tasks`/`graph`/`plan`/`consistency`/`freshness`/`budget`) in one envelope: `{status, data, errors}` |
| `inertia-forge preflight [--path DIR] [--tests DIR]` | composite readiness gate: clean tree + active plan + arch (0 P0) + consistency (+ tests); exits 1 on any fail |
| `inertia-forge validate-store` | integrity-check the `.forge` JSON stores (shape, task fields, ids, statuses) |
| `inertia-forge dead-code [path] [--strict]` | project-wide dead-symbol finder — top-level defs never referenced anywhere (defs from src, refs from src+tests); advisory P2 |
| `inertia-forge learn synthesize` | cluster captured insights by tag into themes (deterministic, no model) |
| `inertia-forge review [path] [--since REF]` | deterministic review: debug leftovers (P1: breakpoint/pdb/console.log/debugger), TODO/FIXME/HACK markers + hardcoded endpoints (P2); git-changed by default |
| `inertia-forge diff [--since REF]` | structured change view — per-file +/- lines and role, rolled up |
| `inertia-forge state [--done/--next/--log]` | session-continuity ledger (+ history) |
| `inertia-forge log [-n N] [--claims]` | view the audit trail (gate events / claims) |
| `inertia-forge pack` | bundle state + plan + tasks + audit → `.forge/context_pack.md` |
| `inertia-forge read <skill>` | mark a skill's methodology doc as read (`doc_reading` mode) |
| `inertia-forge intent "<text>"` | rule-based intent → plan type + suggested skill |
| `inertia-forge ignite <backlog.md>` | set a backlog in motion → plan + tasks + suggested agent |
| `inertia-forge agents [show/install]` | the bundled INERTIA agent roster |
| `inertia-forge memory add/show/list <agent>` | per-agent persistent memory (`.claude/agent-memory/`) |
| `inertia-forge capabilities [--json]` | discovery manifest — the whole toolkit for an LLM to read |
| `inertia-forge orchestrate "<cmd>" …` | run forge commands as a fail-fast pipeline; `select-agent "<task>"` maps work → best-fit agent |
| `inertia-forge metrics add/report/set-rate/velocity/summary` | token usage + cost, plus task throughput (velocity) and a combined task+token summary |
| `inertia-forge compaction snapshot/check/recover/cleanup` | freeze/restore context across a Claude Code compaction — numbered, recoverable snapshots |
| `inertia-forge benchmark [path]` | time the forge's own operations |
| `inertia-forge feature <name> [--no-branch]` | start a feature: git branch + plan + task + next |
| `inertia-forge learn <text> [--tag T]` / `learn list/search` | capture/list/search insights (`.forge/knowledge.jsonl`) |
| `inertia-forge standup [--since]` | daily summary: git commits + tasks + last/next + tokens |
| `inertia-forge config get/set/unset/list/validate` | typed forge settings (`.forge/config.json`) + JSON/known-key validation |
| `inertia-forge contain on/off/set/check/status` | file-access tiers (blocked/readonly/readwrite) for contained sessions |
| `inertia-forge sandbox status/init/check` | command policy — block catastrophic ops, flag risky ones (gate-enforced) |
| `inertia-forge timer start/stop/status/report` | work-time tracking |
| `inertia-forge cache set/get/list/rm/clear` | context blob cache (`.forge/cache/`) |
| `inertia-forge subagent list/create/show/validate/rm` | manage Claude Code subagent definitions |
| `inertia-forge template new/list` | scaffold a forge-ready project |
| `inertia-forge migrate status/run` | versioned `.forge` schema migrations |
| `inertia-forge gaps [src]` | deterministic gap detector — skills w/o docs, tasks w/o AC, modules w/o tests |
| `inertia-forge release validate-versions / checklist` | version-consistency check + release readiness |
| `inertia-forge sprint start/add/complete/list` | group tasks into named sprints |
| `inertia-forge feedback add/list` | capture process feedback (`.forge/feedback.jsonl`) |
| `inertia-forge install-hook` | install a native git pre-commit running the gate |
| `inertia-forge wizard` | one-command guided onboarding (install + health + the loop) |
| `inertia-forge audit <sibling-repo>` | cross-repo impact — shared contracts a sibling consumes + its health |
| `inertia-forge mcp serve/tools` | MCP server exposing the forge's tools to any client |
| `inertia-forge banner` / `logo [--variant full/compact/tiny]` | the INERTIA atom + wordmark — the forge's branded marks |
| `inertia-forge statusline` | Claude Code status segment: `⚛ INERTIA forge · <state>` (reads status JSON on stdin) |
| `inertia-forge init` | install the Claude Code enforcement hooks (gate · stop · compact · containment) |

`arch` and `file_analysis` evidence share the same AST-backed rules, so a gate
can't pass on code that hides a 200-line function or 30 functions in one file.

### Beyond skills — project gates
`inertia-forge check` enforces project invariants (architecture limits + secret
scan + optional tests) **without** a skill session — a session-less gate you can
drop into a pre-commit hook or CI to fail the build on debt or a leaked secret.
This extends the forge from "enforce a skill's methodology" to "enforce the
project's quality bar."

Use it as a **pre-commit hook** in any repo:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/JdogShawn/inertia-forge
    rev: v0.2.0
    hooks:
      - id: inertia-forge-check     # arch + secrets gate
      - id: inertia-forge-sweep     # unused-import sweep
```

`inertia-forge init` also wires a **PreCompact** hook so the forge auto-`pack`s
your context before a Claude Code compaction — continuity survives the squeeze.

---

## The look — INERTIA's visual language

The forge wears INERTIA's identity: the **atom sigil** (orbits of motion around a
still core), the motion-teal → violet palette (`#00FFD1 → #00C9A7 → #a78bfa`),
and orbital status marks (`◉` filled, `○` hollow, `✓`/`▲`/`✗` seals). `status`,
`doctor`, `check`, `arch`, and `task list` all render through one branded kit, so
the whole CLI reads as a single instrument.

It's **zero-dependency and honest about the terminal**: truecolor when advertised,
clean ASCII when not, and fully silent under `NO_COLOR` or a pipe. Every glyph has
an ASCII twin, so a narrow encoding (Windows cp1252) degrades instead of crashing.
`INERTIA_FORGE_LIGHT=1` swaps in higher-contrast tones for light terminals.

```bash
inertia-forge banner          # the full atom + I N E R T I A  F O R G E
inertia-forge logo --variant tiny   # just ⚛
```

### See the forge in your footer — the statusLine

`inertia-forge init` wires a **Claude Code statusLine** so the forge sits in the
footer next to your model, branch, and folder — proof it's installed and live:

```
⚛ INERTIA forge · ◉ T1.2 · 3/8      # an active task
⚛ INERTIA forge · ▣ 2 gates sealed  # a session holding blocking gates
⚛ INERTIA forge · ▢ ready           # installed, idle
```

It reads Claude Code's status JSON from stdin (session id, model, workspace),
renders one ANSI line, and never crashes. Already have a statusLine? `init`
leaves yours untouched — add the forge segment by hand instead:

```json
"statusLine": { "type": "command", "command": "inertia-forge statusline", "padding": 0 }
```

The toolkit is importable, too — `from inertia_forge import paint, banner,
mini_header`, plus `inertia_forge.ui` (`rule`/`panel`/`kv`/`progress_bar`/`ok`…),
`inertia_forge.glyphs`, and `inertia_forge.spinner` for your own forge-flavored CLIs.

---

## Evidence modes

Each skill picks how a phase is proven, in `skill_definitions.yaml`:

| mode | what it proves | for |
|---|---|---|
| `file_analysis` | deterministic code analysis of the target's `.py` files (built-in arch rules: file size, function length, stubs, broad-except, wildcard imports, …) | skills that **produce/modify code** |
| `stamped` | SHA-256 methodology stamp — the phase ran | skills whose output is **insight/findings**, not code (review, audit, investigation) |
| `enforcer` | dispatch to a **registered** per-skill enforcer; falls back to `stamped` if none | custom adversarial / structured checks |
| `task_management` | real plan/task/AC state in the forge's **own native store** (zero deps) | planning / task-lifecycle skills |
| `doc_reading` | the skill's methodology doc was actually read (`inertia-forge read <skill>`) | skills you must not run blind |

Per-phase overrides via `phase_evidence:` (e.g. a code skill whose planning phase should gate on task state).

```python
# enforcer mode is pluggable:
from inertia_forge import register_enforcer
register_enforcer("custom_review", MyEnforcer)   # cls(target); record_step/phase(...)
```

---

## Native task management (`task_management` mode)

The forge ships its **own** plan/task store at `.forge/forge_tasks.json` — no external tools. Skills on `task_management` mode gate on this real state, so a planning gate can't close until tasks actually exist (well-formed IDs, acceptance criteria, a verification command), and a `start_task` gate can't close until the active task is genuinely `done` with all AC met.

```bash
inertia-forge task plan  --type feature --title "Checkout v2"
inertia-forge task add   T1.1 --title "Cart totals" --complexity 8 \
                         --ac "totals correct" --ac "tests pass" --verify "pytest tests/cart"
inertia-forge task start T1.1          # active + in_progress
inertia-forge task ac    T1.1 --all    # check off acceptance criteria
inertia-forge task done  T1.1          # refuses unless every AC is met
inertia-forge task list
```

Verifier rules (phase-keyed, so any skill using these step names is gated): `budget_check` (every task estimated 0–100), `create_plan` (a valid-typed plan exists), `add_tasks` (≥1 well-formed task with AC + verification), `preflight` (active task is `in_progress`), `complete` (active task `done`, all AC met).

---

## Agents & skills — the forge is *for LLMs to use*

The forge gates the work; **agents** are the roles an LLM adopts, **skills** are
the methodology it follows. `inertia-forge init` installs both into `.claude/`.

**The INERTIA agent roster** (`.claude/agents/`):

| agent | role |
|---|---|
| **Vector** | planning & architecture — intent → gated plan + tasks (read-only) |
| **Piston** | implementation — test-first, drives a task to green |
| **Caliper** | code review — measures a change precisely, reports (read-only) |
| **Bastion** | pre-execution security gate — **blocks** dangerous ops |
| **Sentinel** | security audit — scans & reports (read-only) |
| **Gauge** | QA — proves real behavior with tests |
| **Lattice** | cross-cutting — maps how a change ripples across modules |

**Skill methodology docs** (`.claude/skills/<name>/SKILL.md`) ship for every
gated skill (implementing-with-tdd, reviewing-code, security-audit, …). A skill
can require its doc be *read* before its gates count, via `doc_reading` mode +
`inertia-forge read <skill>`.

`inertia-forge init` installs the full kit into a project: the 7 agents, the
skill docs, **slash commands** (`/ignite` · `/chart` · `/drive` · `/calibrate` ·
`/fortify` · `/prove` · `/trace` · `/map` · `/launch`), the **architecture
rules** doc, **per-agent memory**
(`.claude/agent-memory/`), and a forge-aware **CLAUDE.md** + `.forge/context/`
docs — nothing overwritten if it already exists.

```bash
inertia-forge agents              # list the roster
inertia-forge agents show piston  # read an agent's role
inertia-forge memory show piston  # what Piston has learned here
inertia-forge capabilities        # the whole toolkit, for an LLM to discover
```

---

## Configure your own skills

Resolution order (first hit wins):

1. `$INERTIA_FORGE_SKILLS=/path/to/skills.yaml`
2. `./forge_skills.yaml`
3. `./.forge/skills.yaml`
4. the packaged generic starter

```yaml
my_review:
  evidence_mode: stamped
  steps: [read, check_correctness, check_security, verdict]
  gates:
    check_correctness: blocking
    verdict: blocking
```

---

## Claude Code enforcement (hooks)

```bash
cd /path/to/your/project   # IMPORTANT: run init from your project root —
inertia-forge init         # hooks install into THIS directory's .claude/
```

> `inertia-forge init` is directory-scoped: it writes `.claude/hooks/` and patches `.claude/settings.json` in the **current** directory. Always `cd` into the project you want enforced first. It's idempotent — safe to re-run after upgrades.

This wires four hooks so the forge enforces itself inside Claude Code:

- **UserPromptSubmit** → inject the active-session banner; auto-start a session when you type `/<skill>`
- **PreToolUse(Bash)** → block any escape command (`close`, `abandon`, direct `.forge/` writes) — `record-phase` is the only sanctioned forge command
- **Stop** → refuse to stop while blocking gates remain

Sessions are **owner-scoped**: a session belongs to the Claude tab that started it, so parallel tabs never trap or suppress each other. Orphaned sessions from a crashed tab expire after 24h and never block a *different* tab.

---

## How it can't be cheated

- **No manual close / no abandon.** The only close path is auto-close inside `record-phase`.
- **Real evidence.** `file_analysis` hashes the actual bytes of the target's `.py` files; an empty/missing target is a P0.
- **P0 keeps the gate open.** A phase that recorded findings does *not* satisfy its gate.
- **No bypass stamps.** Evidence hashes starting with `manual_release`/`pending`/`stub`/… are rejected.
- **No fake phases.** Phase names outside the skill's step list are P0 `unknown_phase`.

---

## License

MIT. (Extracted from the INERTIA forge.)
