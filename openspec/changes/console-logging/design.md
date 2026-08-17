## Context

All logging configuration lives in one module-level, import-time block in `config.py`:
`logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format=...)`. `filename=` and `handlers=`
are mutually exclusive arguments to `basicConfig`, so adding a console sink means switching to an
explicit `handlers=[...]` list. `basicConfig` is not idempotent by default (no `force=True`), and
`config.py` is imported by `app.py`, `cli.py` (transitively via `recorder.py`), and three adapter
modules — so whatever change is made here must not risk attaching duplicate handlers on repeated
import in the same process, including under pytest.

`worker.warm_up()` currently calls `transcribe_full()` with no logging at all; HF Hub download
progress bars are explicitly disabled (`HF_HUB_DISABLE_PROGRESS_BARS=1`) and `mlx_whisper.transcribe`
is called with `verbose=None` to suppress its own tqdm bar (since `verbose=True` would print
transcribed text). See proposal.md for the motivating gap.

## Goals / Non-Goals

**Goals:**
- Console output reflects the same records as the file log, without duplicating configuration logic.
- No behavior change to *what* is logged today (paste outcomes, exceptions, startup diagnostics) —
  only *where* it's also emitted, plus the new model-load and trigger-armed records.

**Non-Goals:**
- No CLI flags. The repo has zero `argparse` usage today; `cli.py`'s `float(sys.argv[1])` positional
  parse would break if a flag were introduced, and an env var is more consistent with the existing
  `LOCAL_DICTATION_LOG_DIR` pattern.
- No structured/JSON logging, no log rotation, no remote log shipping — out of scope for this change.
- No change to third-party logger quieting (`httpx`/`httpcore`/`urllib3`/`huggingface_hub`/`filelock`
  stay at `WARNING`).

## Decisions

- **Handler wiring**: replace `basicConfig(filename=...)` with
  `basicConfig(handlers=[FileHandler(LOG_FILE), StreamHandler(sys.stderr)], level=..., format=...)`.
  Alternative considered: attach a second handler manually via `logging.getLogger().addHandler(...)`
  outside `basicConfig` — rejected because it's two code paths doing one job; a single `handlers=`
  list keeps the file and console sinks symmetric (same formatter, same level) with one call.
- **Stream choice**: stderr, not stdout. `cli.py` prints the transcription result to stdout; keeping
  logs off stdout means `local-dictation-dictate` stays pipeable (`... | some-command` sees only the
  transcription, per the new spec's "never on stdout" requirement).
- **Level source**: read `LOCAL_DICTATION_LOG_LEVEL` (new env var) via
  `getattr(logging, os.environ.get("LOCAL_DICTATION_LOG_LEVEL", "INFO").upper(), logging.INFO)`,
  falling back to `INFO` for an unrecognized value rather than raising at import time — a typo in the
  env var should degrade gracefully, not crash the app before it starts.
- **Cache-status detection**: check for the presence of the model's Hugging Face Hub cache directory
  (derived from `config.MODEL`, e.g. via `huggingface_hub.try_to_load_from_cache` or an equivalent
  existence check) before calling `transcribe_full()` in `warm_up()`, to log cached-vs-downloading
  without introducing a new dependency (`huggingface_hub` is already transitively present via
  `mlx-whisper`). If that lookup proves unreliable across `huggingface_hub` versions, fall back to
  logging the model name and elapsed time only, without a cached/downloading claim — a slightly less
  informative record beats a wrong one.
- **No filesystem paths in new records**: the model-load and trigger-armed records log only the model
  repo name, a cached/downloading indicator, and durations — never the HF cache path or any other
  filesystem path — per AGENTS.md's "no user-specific paths" boundary. This is a stricter reading
  than `app.py`'s existing `sys.executable` startup record, which is out of scope for this change.

## Risks / Trade-offs

- [Mirroring the log to a terminal widens exposure beyond a user-only file — scrollback buffers,
  screen shares, terminal multiplexer logs] → No new call sites introduced by this change log
  sensitive content; existing higher-risk emitters (`paste.py`'s raw `osascript` stdout/stderr,
  `worker.py`'s `log.exception(...)` tracebacks) are reviewed as part of this change to confirm they
  don't already carry transcript fragments, but are not being newly created by it.
- [`basicConfig` reconfiguration could silently no-op or duplicate handlers if `config` is imported
  more than once in a process, e.g. under test collection] → Cover this with a unit test that
  reimports `config` (or calls a `configure_logging()` extraction) and asserts exactly one
  `FileHandler` and one `StreamHandler` are attached, not one per import.
- [Cache-status detection touches `huggingface_hub` internals that may change between versions] →
  Guarded by the fallback decision above (name + elapsed time only, no claim) if the cache check
  raises or returns an unexpected type.
