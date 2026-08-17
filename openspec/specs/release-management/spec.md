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
The project SHALL document a local release command that creates the version/changelog commit and
version tag without automatically publishing a distribution or creating a hosted release.

#### Scenario: Local release execution
- **WHEN** a developer runs the documented release command on a clean main checkout with qualifying
  commits
- **THEN** package metadata and changelog are versioned and a matching `v{version}` tag is created
