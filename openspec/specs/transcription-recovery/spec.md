# transcription-recovery Specification

## Purpose

Lets users recover a completed recording when local transcription temporarily fails instead of
silently losing the captured audio.

## Requirements

### Requirement: Retriable transcription failures
The system SHALL retry a transcription exception once automatically and retain the recording when
the retry also fails.

#### Scenario: Transient failure succeeds on retry
- **WHEN** a transcription attempt raises an exception and the immediate retry succeeds
- **THEN** the result is delivered normally without requiring user intervention

#### Scenario: Failure persists after automatic retry
- **WHEN** both the original transcription attempt and its automatic retry raise exceptions
- **THEN** the system retains the captured audio and exposes retry and discard controls

### Requirement: Manual failure recovery
The system SHALL allow a user to retry or discard each retained failed recording.

#### Scenario: User retries failed dictation
- **WHEN** the user selects retry for a retained failed recording
- **THEN** the system transcribes that recording again and delivers a successful result normally

#### Scenario: User discards failed dictation
- **WHEN** the user selects discard for a retained failed recording
- **THEN** its audio is released and it is no longer offered for retry
