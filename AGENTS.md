# local-dictation agent guide

local-dictation is an experimental, source-only macOS dictation application. It records only while
the user has started dictation, transcribes with a local Whisper model, and can paste the result into
the focused app. Treat microphone input, clipboard content, and macOS automation permissions as
sensitive user data.

## Required context

Before non-trivial work, read this file, `openspec/config.yaml`, every current spec relevant to the
affected behavior, and any active matching change under `openspec/changes/`. Then read the relevant
source and tests. Current specs describe intended behavior; source and tests describe implementation.
Report and resolve a mismatch rather than silently choosing one.

## Development workflow

- Discuss a substantive proposal in an issue before opening a pull request.
- Use a branch and pull request for every change. Worktrees are a local-development option, not a
  contributor requirement.
- Behavior, privacy, permissions, security, dependency, supported-environment, packaging, and
  release-policy changes require a complete OpenSpec change in the same pull request.
- Keep code, tests, current specs, README, configuration, privacy, and permission documentation in
  agreement. A substantive mismatch blocks merge.
- A critical security fix may be shipped through the protected pull-request path first; record and
  archive its OpenSpec change immediately afterward.

## Environment and checks

Supported development baseline: macOS on Apple Silicon with Python 3.13. Use the repository lockfile
for local and CI installs. Unit tests must not access a real microphone, clipboard, event tap,
Automation permission, desktop session, or Whisper model download. Integration/manual checks may
require the documented macOS permissions and cached model.

## Safety boundaries

- Do not log transcribed text, clipboard values, raw audio, credentials, or user-specific paths.
- Do not add cloud transcription, telemetry, accounts, or API keys without an approved OpenSpec
  privacy/security change.
- Do not use a real paste-injection implementation in automated tests; inject a stub instead.

## Releases

Use Conventional Commits. Routine tags/releases are created by Python Semantic Release after protected
main merges; do not publish to PyPI. Changes to release policy or compatibility require OpenSpec.
