# Investigating

> Root-cause analysis. Gates `observe`, `deduce`, `verify`. Evidence mode:
> `stamped` (output is a diagnosis, not code). Agent: any — this is a discipline.

## When to use
A bug whose cause isn't obvious; a fix that keeps returning; two explanations that
both seem plausible; anything where you'd otherwise guess.

## The phases

### 1. observe  ⟂ blocking — data before theory
State the symptom in one sentence: what was expected, what occurred, the gap.
Then gather **evidence**, not theories: read the actual code, run the actual
command, check the actual value. Tag each fact VERIFIED / REPORTED / ASSUMED.
Never let a conclusion rest on an ASSUMED fact — upgrade it first.

### 2. hypothesize
Generate at least **three** genuinely different explanations; force one improbable
candidate. Assign each a prior. State what evidence would raise, lower, or
eliminate it.

### 3. deduce  ⟂ blocking
Eliminate hypotheses that conflict with VERIFIED evidence. Apply the **negative
inference**: what *should* be present but isn't? Mark the convergence point only
when evidence — not conviction — decides it.

### 4. verify  ⟂ blocking
Before shipping the diagnosis, try to **prove yourself wrong**. What evidence would
falsify it? If you can't find any, your investigation is too narrow. Then state the
smallest fix that addresses the root cause (not the symptom) and how to confirm it.

## Done
A root cause established on VERIFIED evidence, the alternatives eliminated by fact,
and a surgical fix with a verification step.
