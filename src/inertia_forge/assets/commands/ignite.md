---
description: Set a backlog in motion — ingest it into the forge and begin.
---

Run `inertia-forge ignite $ARGUMENTS` to parse the backlog into the forge's plan
and task store, then act on the result:

1. Review the ingested tasks (`inertia-forge task list`) and the suggested agent.
2. For each task in order, run **/drive** (Piston) → **/calibrate** (Caliper).
3. When the plan is complete, run **/launch**.

The backlog is now tracked deterministically; the forge gates every task to green.
