## Why

The repository is ready for a public research-preview release, but its existing Git history is
private development history and contains context that must not become public. A single, audited
public root commit is safer and easier to review than rewriting that history.

## What Changes

- Create a new public Git repository from the audited current snapshot, with exactly one root commit.
- Use the maintainer's GitHub noreply identity for that root commit.
- Align public release documentation and configuration with the automated GitHub-release policy;
  publishing remains source-only and never publishes to PyPI.
- Validate the public snapshot before pushing, then replace the normal checkout with a verified
  clone from the new public remote.
- **BREAKING**: Delete the former private checkout only after the public clone and GitHub controls
  have been verified. The existing vault archive remains the historical record.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This is a publication-history and operational-documentation migration; application behavior
does not change.

## Impact

The repository metadata, documentation, release configuration, GitHub settings, and local checkout
transition are affected. No application API, dependency, or runtime behavior changes.
