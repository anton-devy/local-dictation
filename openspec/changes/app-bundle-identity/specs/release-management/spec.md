## MODIFIED Requirements

### Requirement: Intentional local release

The project SHALL run its release process automatically in CI, gated by Conventional Commit type
prefix on merge to the protected `main` branch, and that automated CI process SHALL NOT publish a
distribution package (e.g. to PyPI) or produce an application bundle. A developer MAY build a macOS
`.app` bundle locally, on demand, outside of CI; doing so is not publication and is not restricted by
this requirement.

#### Scenario: Local release execution

- **WHEN** a pull request whose merge commit message starts with `fix` or `feat` passes required
  checks and merges to `main`
- **THEN** the release workflow versions package metadata and the changelog and creates a matching
  `v{version}` Git tag and GitHub release, without publishing to PyPI or producing an app bundle

#### Scenario: Non-qualifying merge does not release

- **WHEN** a merge commit message does not start with `fix` or `feat` (e.g. a `docs:` or `chore:`
  commit)
- **THEN** no release is created

#### Scenario: Developer builds a local app bundle

- **WHEN** a developer runs the project's local `.app` bundle build script on their own machine
- **THEN** this is permitted and outside the scope of this requirement, since the automated release
  process in CI neither performs nor is affected by that local build
