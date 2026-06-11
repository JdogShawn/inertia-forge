# inertia-forge

**A project-agnostic, deterministic skill-enforcement engine. The only way out is to do the work.**

The forge makes a skill's methodology *mechanically enforced*. Invoking a skill opens a **session** with **blocking gates**. You can't manually close it, you can't skip a gate, and you can't fake evidence — the session auto-closes only when the last blocking gate is recorded with a real, hash-verified result. No escape hatch by design.

Zero LLM calls. Pure deterministic algorithms.

---

## Install

```bash
pip install inertia-forge
# optional: real plan/task/AC gating via bpsai-pair
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

---

## Evidence modes

Each skill picks how a phase is proven, in `skill_definitions.yaml`:

| mode | what it proves | for |
|---|---|---|
| `file_analysis` | deterministic code analysis of the target's `.py` files (built-in arch rules: file size, function length, stubs, broad-except, wildcard imports, …) | skills that **produce/modify code** |
| `stamped` | SHA-256 methodology stamp — the phase ran | skills whose output is **insight/findings**, not code (review, audit, investigation) |
| `enforcer` | dispatch to a **registered** per-skill enforcer; falls back to `stamped` if none | custom adversarial / structured checks |
| `task_management` | real plan/task/AC state (needs `[paircoder]` extra) | planning / task-lifecycle skills |

Per-phase overrides via `phase_evidence:` (e.g. a code skill whose planning phase should gate on task state).

```python
# enforcer mode is pluggable:
from inertia_forge import register_enforcer
register_enforcer("custom_review", MyEnforcer)   # cls(target); record_step/phase(...)
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
cd your-project
inertia-forge init        # installs hooks into .claude/ and wires settings.json
```

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
