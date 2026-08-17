## MODIFIED Requirements

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
