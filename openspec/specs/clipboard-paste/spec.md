## Purpose

Auto-pastes an accepted transcription into the frontmost application, with safe clipboard
behavior, a focus-changed guard, honest handling of paste failures, and a
permission-independent fallback so the user always has a way to reach the text.

## Requirements

### Requirement: Auto-paste into the frontmost application
The system SHALL automatically paste an accepted transcription result into the frontmost
application after transcription completes, in addition to placing it on the clipboard.

#### Scenario: Successful auto-paste
- **WHEN** a transcription result is accepted and the frontmost application has not changed
  since the recording stopped
- **THEN** the transcribed text is pasted into the frontmost application's current insertion
  point

### Requirement: Dictated text persists on the clipboard after paste
The system SHALL leave the dictated text on the clipboard after an auto-paste operation
rather than attempting to restore the user's prior clipboard contents, since there is no
reliable way to detect when the target application has finished reading the pasteboard —
restoring on a fixed delay risks overwriting the clipboard before the target application has
actually consumed the paste, causing stale content to be inserted instead of the dictation.

#### Scenario: Clipboard holds the dictation after a successful paste
- **WHEN** an auto-paste operation completes
- **THEN** the clipboard continues to hold the dictated text rather than being reverted to
  its prior contents

#### Scenario: Dictated text preserved if paste is skipped
- **WHEN** auto-paste is skipped (see the focus-changed guard) or disabled
- **THEN** the transcribed text remains on the clipboard for manual pasting, and is not
  silently discarded, and is not marked transient (so clipboard-manager history tools can
  still surface it)

### Requirement: Last dictation recovery
The system SHALL retain the most recent transcription result in memory, independent of
clipboard state, and provide a way for the user to copy it to the clipboard on demand.

#### Scenario: Recovering the last dictation
- **WHEN** the user requests the last dictation (e.g. via a menu item)
- **THEN** the most recent transcription result is copied to the clipboard, regardless of
  what has happened to the clipboard since

### Requirement: Focus-changed paste guard
The system SHALL skip auto-paste, leaving the transcribed text on the clipboard instead, if
the frontmost application changes between when recording stopped and when the transcription
is ready to paste.

#### Scenario: Frontmost app unchanged
- **WHEN** the frontmost application at paste time is the same as the frontmost application
  when recording stopped
- **THEN** auto-paste proceeds normally

#### Scenario: Frontmost app changed
- **WHEN** the frontmost application at paste time differs from the frontmost application
  when recording stopped
- **THEN** auto-paste is skipped, the transcribed text remains on the clipboard, and the
  user is notified

### Requirement: Auto-paste configurable
The system SHALL allow the user to disable auto-paste via configuration, in which case
transcribed text is only copied to the clipboard.

#### Scenario: Auto-paste disabled in configuration
- **WHEN** auto-paste is disabled in the configuration
- **THEN** transcribed text is copied to the clipboard only, and no paste keystroke is
  synthesized

### Requirement: Required permission for auto-paste
The system SHALL use macOS Automation permission to ask System Events to synthesize a paste
keystroke and SHALL document this requirement. Input Monitoring is separately required for
global key capture; a working trigger does not prove auto-paste permission is granted.

#### Scenario: Accessibility not granted
- **WHEN** the calling process does not have Accessibility trust
- **THEN** the paste attempt fails with an identifiable permission error rather than
  silently doing nothing, the dictated text remains on the clipboard, and the user is
  notified (see "Paste failure handling" below)

### Requirement: Paste failure handling
The system SHALL distinguish a permission-related paste failure from other paste failures,
notify the user with an actionable message in either case, and always leave the dictated
text on the clipboard when a paste does not succeed.

#### Scenario: Permission-related failure
- **WHEN** a paste attempt fails because the calling process lacks the required permission
- **THEN** the user is notified that a permission is needed for auto-paste, and the text
  remains on the clipboard

#### Scenario: Other failure
- **WHEN** a paste attempt fails for a reason other than a permission problem
- **THEN** the user is notified that the paste failed, and the text remains on the
  clipboard

### Requirement: Fallback text display near the cursor
The system SHALL show the transcribed text in a floating, non-activating display near the
user's cursor whenever a dictation's paste does not land automatically (skipped due to a
focus change, or failed for a permission or other reason), so the user always has an
immediate, visible way to see and manually paste the text, independent of clipboard state
and requiring no additional system permission.

#### Scenario: Paste did not land
- **WHEN** a dictation's paste outcome is anything other than a successful automatic paste
  (or auto-paste being intentionally disabled)
- **THEN** the transcribed text appears in a floating display near the cursor and
  automatically disappears after a few seconds, without requiring any additional
  permission

#### Scenario: Successful paste does not show the fallback display
- **WHEN** a dictation is auto-pasted successfully, or auto-paste is disabled by
  configuration
- **THEN** the fallback display does not appear
