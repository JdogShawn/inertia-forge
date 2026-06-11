---
description: Map the ripple — Lattice traces how a change propagates across modules.
---

Adopt **Lattice** (`.claude/agents/lattice.md`).

Map the blast radius of: **$ARGUMENTS** (a change, a symbol, an API).

1. Find every consumer of what changed — Grep the symbol, route, event, schema.
2. Trace data/control flow across module boundaries by hand, with `file:line`.
3. Surface contract breaks, dependency conflicts, and wiring gaps (built-but-
   unwired, wired-but-unused).
4. Name the second-order effects: what breaks one hop away, two hops away —
   migrations, env vars, CI, deploy steps implied.

"It works locally" is not "it integrates." Prove the seams hold; hand precise
findings to Vector/Piston.
