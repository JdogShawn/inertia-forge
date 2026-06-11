# inertia-forge

**A project-agnostic, deterministic skill-enforcement engine. The only way out is to do the work.**

The forge makes a skill's methodology *mechanically enforced*. Invoking a skill opens a **session** with **blocking gates**. You can't manually close it, you can't skip a gate, and you can't fake evidence — the session auto-closes only when the last blocking gate is recorded with a real, hash-verified result. No escape hatch by design.

Zero LLM calls. Pure deterministic algorithms.

---

## Install

```bash
pip install inertia-forge
# optional extra: the bpsai-pair task backend (native task_management needs nothing)
pip install "inertia-forge[paircoder]"
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
| `inertia-forge skills` / `skills validate` | list the registry / validate it's well-formed |
| `inertia-forge start <skill> <target>` | open a forge session |
| `inertia-forge record-phase <phase> <target>` | record a phase (auto-closes on all-green) |
| `inertia-forge status` | forge session + plan + task progress + last/next |
| `inertia-forge arch <path>…` | deterministic architecture check (file size, **function length, functions/file, imports/file**, stubs, broad-except, …) — exits 1 on any P0 |
| `inertia-forge verify [dir]` | run pytest on a target |
| `inertia-forge task …` | native task store: `plan`/`add`/`start`/`ac`/`done`/`list`/`show`/`budget` |
| `inertia-forge state --done "…" --next "…"` | session-continuity ledger |
| `inertia-forge init` | install the Claude Code enforcement hooks |

`arch` and `file_analysis` evidence share the same AST-backed rules, so a gate
can't pass on code that hides a 200-line function or 30 functions in one file.

---

## Evidence modes

Each skill picks how a phase is proven, in `skill_definitions.yaml`:

| mode | what it proves | for |
|---|---|---|
| `file_analysis` | deterministic code analysis of the target's `.py` files (built-in arch rules: file size, function length, stubs, broad-except, wildcard imports, …) | skills that **produce/modify code** |
| `stamped` | SHA-256 methodology stamp — the phase ran | skills whose output is **insight/findings**, not code (review, audit, investigation) |
| `enforcer` | dispatch to a **registered** per-skill enforcer; falls back to `stamped` if none | custom adversarial / structured checks |
| `task_management` | real plan/task/AC state in the forge's **own native store** (zero deps) | planning / task-lifecycle skills |
| `paircoder` | real plan/task/AC state via **bpsai-pair** (needs the `[paircoder]` extra) | teams already on bpsai-pair |

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

**Already on bpsai-pair?** Use `evidence_mode: paircoder` instead (install `inertia-forge[paircoder]`) and the same gates verify bpsai-pair's `.paircoder/` state. Both backends ship; pick per skill.

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
