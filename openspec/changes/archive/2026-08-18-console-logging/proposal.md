## Why

Logging today is file-only (`logging.basicConfig(filename=...)` in `config.py`, no `StreamHandler`
anywhere), and the one long-running startup step — loading the ~1.5GB Whisper model in
`worker.warm_up()` — emits no records at all, because Hugging Face's download progress bars are
deliberately suppressed. Starting `local-dictation` from a terminal on a cold cache looks
indistinguishable from a hang for minutes at a time, with nothing on screen and nothing in the log
file until the first paste happens. A live console diagnostic during startup and model load closes
that gap without changing what the file log records.

## What Changes

- Console log output (stderr) mirrors the existing file log, on by default, controlled by a new
  `LOCAL_DICTATION_LOG_LEVEL` env var (default `INFO`) alongside the existing
  `LOCAL_DICTATION_LOG_DIR`.
- `worker.warm_up()` gains log records: model name, whether it is already cached or being
  downloaded, and elapsed load time on completion.
- `app.py` logs a record once the global-hotkey trigger is armed and ready.
- `local-dictation-dictate`'s stdout (the transcription output) is unaffected — new log records are
  stderr-only.
- README's "Privacy and diagnostics" section is updated to describe console output alongside the
  file log.

## Capabilities

### New Capabilities
- `logging-diagnostics`: Defines what local-dictation logs, where (file and console), at what
  default verbosity, and the privacy constraints on log content — filling a gap where no
  logging/diagnostics capability spec exists today despite `config.py` already implementing file
  logging.

### Modified Capabilities
None. `idle-unload-lifecycle` and `dictation-pipeline` describe model warm-up and reload behavior but
not its logging; this change adds diagnostics without altering when or how the model loads, so no
existing requirement changes.

## Impact

Affected code: `src/local_dictation/config.py` (logging configuration), `src/local_dictation/worker.py`
(`warm_up()`), `src/local_dictation/app.py` (post-`trigger.start()` confirmation). No new
dependencies, no change to the audio/transcription/paste pipeline, no change to file-log content or
location. README's privacy/diagnostics documentation is updated in the same PR.
