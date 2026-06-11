---
description: Trace the fault to its root — investigate, don't guess.
---

Run the **investigating** methodology (`.claude/skills/investigating/SKILL.md`).

Trace: **$ARGUMENTS** (the symptom, bug, or surprising behavior).

1. **Observe** — state the symptom in one sentence (expected vs occurred). Gather
   evidence, not theories: read the actual code, run the actual command, check the
   actual value. Tag each fact VERIFIED / REPORTED / ASSUMED.
2. **Hypothesize** — at least three genuinely different explanations; force one
   improbable. Assign priors; state what evidence would eliminate each.
3. **Deduce** — eliminate what conflicts with VERIFIED evidence. Apply the
   negative inference: what should be present but isn't?
4. **Verify** — before shipping the diagnosis, try to prove yourself wrong. Then
   propose the smallest fix for the root cause (not the symptom) + how to confirm.

Never let a conclusion rest on an ASSUMED fact.
