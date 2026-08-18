# release-management Specification

## Purpose

Provides a repeatable, automated release process that derives semantic versions from Conventional
Commits on every qualifying merge to the protected `main` branch, while keeping publication scope
(source-only, no PyPI, no app bundle) under explicit maintainer control.

## Requirements

### Requirement: Semantic version derivation
The project SHALL derive its next semantic version from Conventional Commit messages and stamp the
selected version into package metadata.

#### Scenario: Dry-run release
- **WHEN** a developer runs the documented release dry-run command on a clean checkout
- **THEN** the command reports the version it would produce without changing repository files or
  tags

### Requirement: Intentional local release
The project SHALL run its release process automatically in CI, gated by Conventional Commit type
prefix on merge to the protected `main` branch, and SHALL NOT automatically publish a distribution
package (e.g. to PyPI) or an application bundle.

#### Scenario: Local release execution
- **WHEN** a pull request whose merge commit message starts with `fix` or `feat` passes required
  checks and merges to `main`
- **THEN** the release workflow versions package metadata and the changelog and creates a matching
  `v{version}` Git tag and GitHub release, without publishing to PyPI or producing an app bundle

#### Scenario: Non-qualifying merge does not release
- **WHEN** a merge commit message does not start with `fix` or `feat` (e.g. a `docs:` or `chore:`
  commit)
- **THEN** no release is created

