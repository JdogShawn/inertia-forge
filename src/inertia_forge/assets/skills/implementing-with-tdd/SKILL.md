# Implementing with TDD

> Test-first development. The forge gates `write_failing_test`, `verify_green`,
> and `arch_check`. Agent: **Piston**.

## When to use
Any time you write or change behavior — features, bug fixes, refactors with new
behavior. If you're about to type implementation code, you're in this skill.

## The phases

### 1. write_failing_test  ⟂ blocking
Write a test for the smallest next behavior. Run it. **See it fail for the right
reason** (assertion, not import error). A test that passes immediately tests
nothing.

### 2. write_minimal_code
Write the least code that makes the test pass. No speculative generality. Run the
test; see it go green.

### 3. verify_green  ⟂ blocking
Run the full relevant suite — `inertia-forge verify <dir>`. Zero failures. If
something else broke, you're not green.

### 4. refactor
Clean up with tests staying green: names, duplication, structure. Re-run after
each step.

### 5. arch_check  ⟂ blocking
`inertia-forge arch <changed files>`. Fix every P0 (function > 50 lines, file >
400, > 15 functions, stubs). Extract helpers; split modules.

## Recording
After each phase: `inertia-forge record-phase <phase> <target>`. The session
auto-closes when the last blocking gate is green. There is no manual close.

## Done
Behavior covered by tests written *first*, the suite green by direct observation,
and `arch` clean on the diff.
