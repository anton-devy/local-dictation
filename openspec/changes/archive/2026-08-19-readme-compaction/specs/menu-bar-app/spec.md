## MODIFIED Requirements

### Requirement: Descriptive process identity
The menu-bar app SHALL identify itself as `local-dictation` to process-level tooling such as `ps`.

#### Scenario: App is running
- **WHEN** the menu-bar app is launched
- **THEN** `ps` reports its process name (`comm`) as `local-dictation`

#### Scenario: Kernel-level process name may still differ
- **WHEN** the app is run from a source checkout without an `.app` bundle
- **THEN** macOS tools that read the exec'd binary's identity rather than argv (e.g. Activity
  Monitor's Process Name column) MAY still show the underlying interpreter rather than
  `local-dictation` — this is a known limitation of the unbundled distribution, not a defect
