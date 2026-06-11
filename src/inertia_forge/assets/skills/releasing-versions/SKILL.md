# Releasing Versions

> Cut a release safely. Gates `validate_ready` and `security_check`. Agents:
> **Bastion** + **Sentinel** (safety), **Gauge** (tests).

## When to use
Shipping a tagged version to users (PyPI, a registry, a deploy).

## The phases

### 1. validate_ready  ⟂ blocking
- Full suite green on the release commit: `inertia-forge verify --cov`.
- Project gate clean: `inertia-forge check .`.
- Working tree clean; on the release branch; schema current (`inertia-forge migrate
  status`).

### 2. bump_version
Bump the version in exactly one source of truth; let everything else read it.

### 3. update_changelog
What changed, for users — not a commit dump. Note breaking changes loudly.

### 4. security_check  ⟂ blocking
`inertia-forge check` (secrets) + `inertia-forge scan-deps` (CVEs). A leaked
credential or a critical CVE stops the release. Bastion enforces.

### 5. tag_release
Tag the version; let CI build + publish. Verify the artifact installs from the
registry before declaring done.

## Done
A tagged, tested, secret-free, dependency-clean release whose published artifact
has been verified to install — no "should work."
