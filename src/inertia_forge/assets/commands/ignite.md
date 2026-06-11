---
description: Set a backlog in motion — ingest it into the forge and begin.
---

Run `inertia-forge ignite $ARGUMENTS` to parse the backlog into the forge's plan
and task store, then act on the result:

1. Review the ingested tasks (`inertia-forge task list`) and the suggested agent.
2. For each task in order, run **/forge-build** (Piston) → **/forge-review**
   (Caliper).
3. When the plan is complete, run **/forge-ship**.

The backlog is now tracked deterministically; the forge gates every task to green.
