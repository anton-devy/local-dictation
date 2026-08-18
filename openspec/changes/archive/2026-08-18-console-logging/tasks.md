## 1. Logging configuration

- [ ] 1.1 Replace `logging.basicConfig(filename=...)` in `config.py` with a `handlers=[FileHandler,
      StreamHandler(sys.stderr)]` form, keeping the existing format string and third-party quieting
      loop unchanged.
- [ ] 1.2 Read `LOCAL_DICTATION_LOG_LEVEL` (default `INFO`, case-insensitive, invalid value falls
      back to `INFO`) to set the level shared by both handlers.
- [ ] 1.3 Guard against duplicate handler attachment on repeated import of `config` (e.g. `force=True`
      or a reentry-safe `configure_logging()` extraction).

## 2. Model-load and startup diagnostics

- [ ] 2.1 In `worker.warm_up()`, log a record before loading: model name (`config.MODEL`) and
      cached-vs-downloading status, determined without a new dependency.
- [ ] 2.2 In `worker.warm_up()`, log a record after loading completes: elapsed load time.
- [ ] 2.3 In `app.py`, log a record once `trigger.start()` succeeds, confirming the app is armed.
- [ ] 2.4 Confirm no new record includes a filesystem path, transcribed text, clipboard content, or
      raw audio — review against `paste.py`'s `text_len=%d` pattern.

## 3. Tests

- [ ] 3.1 Add a unit test asserting console (stderr) and file handlers are both attached exactly once,
      covering the re-import/duplicate-handler risk from design.md.
- [ ] 3.2 Add a unit test for `LOCAL_DICTATION_LOG_LEVEL` default and override behavior, including an
      invalid value falling back to `INFO`.
- [ ] 3.3 Add a unit test for `warm_up()`'s new log records (cached and not-cached cases) against a
      stubbed `transcribe_full` — no real model download or network access.
- [ ] 3.4 Add a unit test confirming `local-dictation-dictate`'s stdout output contains no log records
      (log records are stderr-only).

## 4. Documentation

- [ ] 4.1 Update README's "Privacy and diagnostics" section to describe console output alongside the
      file log location, and document `LOCAL_DICTATION_LOG_LEVEL`.

## 5. Validation

- [ ] 5.1 `ruff check .`, `pytest tests/unit -q`, `uv build` all pass.
- [ ] 5.2 `openspec validate --all --strict` passes for this change.
- [ ] 5.3 Manual check: cold and warm `local-dictation` startup on this machine shows the expected
      console records on stderr, `local-dictation 2>/dev/null` prints nothing, and
      `~/Library/Logs/local-dictation/local-dictation.log` still receives every record.
