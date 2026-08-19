## ADDED Requirements

### Requirement: App bundle build

The project SHALL provide a committed script that builds a macOS `.app` bundle in py2app alias mode
(referencing the project's installed environment, vendoring nothing) and ad-hoc signs it with a
fixed, stable bundle identifier.

#### Scenario: Bundle is built

- **WHEN** a developer runs the committed build script on a checkout with dependencies installed
- **THEN** a `local-dictation.app` bundle is produced, ad-hoc signed with the identifier
  `com.devant0n.local-dictation`, and the identifier does not change between builds

#### Scenario: Bundle does not vendor the runtime

- **WHEN** the bundle is built
- **THEN** it references the existing Python environment in alias mode rather than freezing or
  vendoring the interpreter, mlx/Metal libraries, or other dependencies

#### Scenario: Rebuilding invalidates TCC grants (documented limitation)

- **WHEN** the bundle is rebuilt, including with no source changes
- **THEN** ad-hoc signing (no Apple-issued certificate) derives the bundle's code identity from a
  hash of its contents, so the rebuilt binary is a distinct, ungranted identity to macOS even though
  its `CFBundleIdentifier` string is unchanged — any previously granted Input Monitoring or
  Automation permission stops working until reset (`tccutil reset`) and re-granted; this is verified
  behavior, documented in the README, not a defect to silently discover

## MODIFIED Requirements

### Requirement: Descriptive process identity

The macOS `.app` bundle SHALL identify itself as `local-dictation` to both process-level tooling
(`ps`) and macOS's process-identity-based UI (Activity Monitor's Process Name column). The
development-only console-script entry point SHALL continue to identify itself as `local-dictation` to
`ps` via argv, without asserting an Activity Monitor claim for that path.

#### Scenario: App is running

- **WHEN** the `.app` bundle is launched
- **THEN** `ps` reports its process name (`comm` and `ucomm`) as `local-dictation`, and Activity
  Monitor's Process Name column shows `local-dictation`

#### Scenario: Kernel-level process name may still differ

- **WHEN** the app is launched via the `local-dictation` console script or
  `python -m local_dictation.app` from a source checkout, without the `.app` bundle
- **THEN** `ps` reports its process name (`comm`) as `local-dictation`, but macOS tools that read the
  exec'd binary's identity rather than argv (e.g. Activity Monitor's Process Name column) show the
  underlying interpreter instead — expected for this development-only path, not a defect
