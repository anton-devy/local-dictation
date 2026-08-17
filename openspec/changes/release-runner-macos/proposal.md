## Why

`release.yml` fails on every qualifying push: it runs on `runs-on: ubuntu-latest`, but
`pyobjc-framework-Quartz`/`pyobjc-framework-Cocoa` are base (non-optional) dependencies that only
build on macOS, so `uv sync --all-extras --locked` always fails there regardless of extras. `ci.yml`
already runs on `macos-14`, matching the project's documented macOS-only supported baseline.

While fixing this, `openspec/specs/release-management/spec.md` was found to be stale relative to
already-documented, actual behavior: it describes releases as a "local process... under explicit
user control" (a developer manually running a release command), but `release.yml` and README's
"Releases" section both already describe an automatic, CI-driven release on every qualifying merge
to `main`. The spec text predates that automation; nothing about actual release behavior is changing
here — only the spec is being brought into agreement with it, per AGENTS.md's "keep specs, README,
and configuration in agreement" rule.

## What Changes

- `release.yml`'s `release` job runs on `macos-14` instead of `ubuntu-latest`.
- `release-management`'s "Intentional local release" requirement is rewritten to describe the actual
  automated, merge-triggered release process (CI-driven, gated by Conventional Commit prefix, no
  PyPI/app-bundle publish) instead of a manually-run local command. The capability's `Purpose` is
  also corrected to match (edited directly in `openspec/specs/release-management/spec.md`, per
  OpenSpec's own guidance for Purpose changes on an existing capability).
- No change to *what* triggers a release, how versions are derived, or the no-PyPI/no-app-bundle
  publication boundary — only the execution environment (this fix) and the spec's description of
  already-existing automation (the drift fix).

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `release-management`: the "Intentional local release" requirement is rewritten to describe the
  automated, CI-triggered release process instead of a manually-run local release command.

## Impact

Affected: `.github/workflows/release.yml` (runner change), `openspec/specs/release-management/spec.md`
(Purpose + requirement text). No dependency, packaging, or publication-boundary change; no change to
the trigger condition or versioning logic in `release.yml` itself.
