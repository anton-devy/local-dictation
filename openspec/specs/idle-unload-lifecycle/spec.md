## Purpose

Reduces idle-time memory footprint by unloading the transcription model from memory after a period of inactivity, and reloading it on the next transcription request with a visible UI cue during the brief reload delay.

## Requirements

### Requirement: Unload model after idle timeout
The system SHALL release the loaded transcription model from memory if no transcription request has been received for a configured idle timeout duration (e.g., 10 minutes).

#### Scenario: Model unloaded after idle period
- **WHEN** the configured idle timeout duration has elapsed since the last completed transcription
- **THEN** the transcription model is released from memory, and subsequent process memory profiling shows the freed footprint

#### Scenario: Idle timer resets on transcription activity
- **WHEN** a transcription request is received (user initiates a recording)
- **THEN** the idle timer is reset, and a just-unloaded model remains loaded (the unload does not occur)

### Requirement: Reload model on demand with UI cue
The system SHALL automatically reload the transcription model on the next transcription request after an idle unload, displaying a visible UI cue to the user during the reload delay so the user understands the app is working.

#### Scenario: First transcription after idle unload
- **WHEN** the user initiates a recording after the model has been unloaded due to idle timeout
- **THEN** the system reloads the model (a brief delay, typically 1-2 seconds), displays a UI cue (e.g., menu-bar state change, HUD flash, or status message), and proceeds with transcription once the model is ready

#### Scenario: Transcription after idle still produces correct results
- **WHEN** transcription completes after a model reload from idle unload
- **THEN** the transcribed text is correct and the output behavior (clipboard, paste, filters) is unchanged from a non-idle transcription

### Requirement: Idle timeout is configurable
The system SHALL allow the idle timeout duration to be configured (e.g., via a config file or menu setting), so users can adjust the balance between memory savings and reload convenience.

#### Scenario: Idle timeout configured to 5 minutes
- **WHEN** the idle timeout is set to 300 seconds
- **THEN** the model is unloaded 300 seconds after the last transcription completes (or does not occur)

#### Scenario: Idle timeout set to never (effectively disabled)
- **WHEN** the idle timeout is set to a very large value (e.g., 24 hours or 0 for disabled)
- **THEN** the model is kept resident indefinitely (original v2 behavior is preserved as an option)

### Requirement: Unload does not interrupt active transcription
The system SHALL NOT unload the model while a transcription is in progress, even if the idle timer fires during transcription.

#### Scenario: Idle timer fires during transcription
- **WHEN** an active transcription is in progress and the idle timeout expires
- **THEN** the idle timer does not trigger an unload; the model remains loaded until transcription completes and the idle timer resets

### Requirement: Complete idle memory release
The system SHALL release the transcription model and reclaim releasable runtime caches after the
configured idle timeout.

#### Scenario: Model unload after startup idle
- **WHEN** the app has completed startup and remains idle for the configured timeout
- **THEN** it unloads the model and clears releasable runtime caches without requiring a prior
  dictation

### Requirement: Idle lifecycle respects outstanding work
The system SHALL not unload the model while recording, transcribing, or holding queued work.

#### Scenario: Idle timer fires with pending work
- **WHEN** the idle timeout elapses while recording or pending transcription work exists
- **THEN** the model remains loaded until the work completes and a subsequent idle timeout elapses
