## Purpose

Defines what local-dictation logs, where diagnostics are emitted (file and console), the default
verbosity and how it is configured, and the privacy constraints on log content, so startup and
model-loading progress are observable without exposing sensitive data.

## ADDED Requirements

### Requirement: Console mirrors file diagnostics by default
The system SHALL emit its diagnostic log records to the process's standard error stream, in addition
to the existing log file, without requiring any flag or environment variable to enable it.

#### Scenario: Running from a terminal shows live diagnostics
- **WHEN** a user starts `local-dictation` or `local-dictation-dictate` from a terminal
- **THEN** log records appear on stderr as they are emitted, and the same records are also written to
  the log file at `~/Library/Logs/local-dictation/local-dictation.log` (or
  `$LOCAL_DICTATION_LOG_DIR` if set)

### Requirement: Console diagnostics never appear on stdout
The system SHALL NOT write log records to standard output.

#### Scenario: CLI output stays pipeable
- **WHEN** a user runs `local-dictation-dictate | some-other-command`
- **THEN** only the CLI's own transcription-result output (language, text, clipboard confirmation)
  reaches the pipe, with no log records mixed in

### Requirement: Log verbosity is configurable via environment variable
The system SHALL read a `LOCAL_DICTATION_LOG_LEVEL` environment variable to set the minimum level of
records emitted to both the file and the console, defaulting to `INFO` when unset.

#### Scenario: Default verbosity
- **WHEN** `LOCAL_DICTATION_LOG_LEVEL` is not set
- **THEN** the system logs at `INFO` level and above to both file and console

#### Scenario: Custom verbosity
- **WHEN** `LOCAL_DICTATION_LOG_LEVEL=DEBUG` is set in the environment before startup
- **THEN** the system logs at `DEBUG` level and above to both file and console

### Requirement: Model load progress is observable
The system SHALL log, for the Whisper model load performed during startup, a record naming the
configured model and indicating whether it is already present in the local cache or is being
downloaded, and a record on completion stating the elapsed load time.

#### Scenario: Cold cache
- **WHEN** the configured model is not yet present in the local model cache and `warm_up()` runs
- **THEN** a log record is emitted before loading begins, naming the model and indicating it is being
  downloaded, and a log record is emitted after loading completes, stating the elapsed time

#### Scenario: Warm cache
- **WHEN** the configured model is already present in the local model cache and `warm_up()` runs
- **THEN** a log record is emitted before loading begins, naming the model and indicating it is
  cached, and a log record is emitted after loading completes, stating the elapsed time

### Requirement: Trigger-armed confirmation is observable
The system SHALL log a record once the global-hotkey trigger has started successfully, confirming the
app is ready to receive the hotkey.

#### Scenario: App startup completes
- **WHEN** the app finishes starting and the global-hotkey trigger begins listening
- **THEN** a log record is emitted confirming the trigger is armed

### Requirement: Diagnostics never include sensitive content
The system SHALL NOT include transcribed text, clipboard content, raw audio data, credentials, or
filesystem paths outside the documented log file location in any log record, on file or console.

#### Scenario: Model-load and trigger records carry no sensitive data
- **WHEN** any log record introduced by this capability is emitted
- **THEN** the record contains only the model repository name, a cached/downloading indicator,
  elapsed durations, and trigger status — never dictated text, clipboard contents, audio samples,
  credentials, or a user-specific filesystem path
