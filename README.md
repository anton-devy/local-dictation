# local-dictation

> **Research preview.** Source-only and experimental; no app bundle, notarization, PyPI package, or
> support SLA. Supported baseline: macOS on Apple Silicon with Python 3.13.

A fully local, on-device macOS speech-to-text dictation app. Press **Control+Shift+D**
(default, configurable) to start listening, speak, press it again to stop — the
transcription (auto-detected English or German) is automatically pasted wherever your
cursor is, and stays on the clipboard afterward either way. If auto-paste can't land for
any reason, a small HUD shows the text right near your cursor so grabbing it is still a
single ⌘V away. No cloud, no API keys; transcription runs entirely on-device via
[mlx-whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper).

## Setup

The project uses modern Python packaging (pyproject.toml + hatchling). First run downloads
the `whisper-large-v3-turbo` model (currently about 1.61 GB) from Hugging Face to the local cache. After that,
everything works offline.

### Installation

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .
```

This installs the `local-dictation` and `local-dictation-dictate` console scripts, plus all
dependencies from `pyproject.toml`.

### Optional: Development Dependencies (for testing)

```bash
pip install -e ".[dev]"
pytest tests/unit/ -v              # Fast unit tests only
pytest tests/integration/ -v       # Full suite (includes real model loading)
```

The integration tests transcribe the committed audio samples in `fixtures/`. If those files
are ever missing, the tests that need them skip with a reminder — run `./fixtures/generate.sh`
to recreate them from macOS `say` voices.

## Privacy and diagnostics

Audio and transcription are processed locally. The only expected outbound network access is the first
model download from Hugging Face. The app does not include telemetry, accounts, or API keys. Dictated
text remains on the system clipboard after use. Diagnostic logs are stored in
`~/Library/Logs/local-dictation/` (or `LOCAL_DICTATION_LOG_DIR`) and must not contain dictated text.

## Releases

Use Conventional Commits (`fix:` for patch, `feat:` for minor, and `feat!:` or a
`BREAKING CHANGE:` footer for major). After a pull request passes required checks and merges to
protected `main`, the release workflow uses Python Semantic Release to create routine Git tags and
GitHub releases. The `chore:` initial public-preview commit is a baseline and does not release.

Releases remain source-only: this project does not publish to PyPI or distribute an app bundle.
Maintainers can inspect the next version locally with:

```bash
semantic-release --noop version
```

## Usage

- **Menu-bar app (recommended):** After installation, run `local-dictation` or
  `python -m local_dictation.app`. Press the trigger combo once to start recording (icon
  turns 🔴, and the microphone is only active while a recording is in progress), press it
  again to stop — the clip is transcribed and, if a text field is focused, pasted
  automatically. A notification shows the detected language and a preview. A **"Copy Last
  Dictation"** menu item recovers the most recent transcription at any time.
- **CLI, fixed-duration recording:** `local-dictation-dictate [seconds]` (default 5s).
  Records, transcribes, copies the result to the clipboard. Simplest way to test the raw
  pipeline.

## Permissions (macOS)

The app needs **three** permissions:

- **Microphone** — required by `sounddevice` to capture audio. Prompted automatically the
  first time recording starts. The mic is only opened while an actual recording is in
  progress and is fully released the instant you stop — it's never active while idle.
- **Input Monitoring** — required to observe the trigger combo globally. macOS does **not**
  always prompt automatically; if pressing the combo does nothing, go to
  **System Settings → Privacy & Security → Input Monitoring** and enable it for your
  terminal app (Terminal.app, iTerm, etc.) or the Python interpreter running the script.
- **Automation** (to control System Events) — required for auto-paste, which is
  synthesized via AppleScript/System Events rather than a raw keystroke API (see "Why
  auto-paste goes through System Events" below). The first time a dictation tries to
  paste, macOS should prompt you to allow this — click Allow. If it doesn't prompt, or if
  you dismissed it, check **System Settings → Privacy & Security → Automation** and make
  sure your terminal app / Python is allowed to control "System Events." If this
  permission is missing, auto-paste fails and a notification tells you so; the
  transcription is still on the clipboard, and a HUD shows the text near your cursor
  either way (see below) — see `AUTO_PASTE` in `config.py` to disable auto-paste attempts
  entirely instead.

The menu bar shows a live **Status** line: Input Monitoring state, plus the outcome of the
last real paste attempt (there's no reliable way to check Automation permission ahead of
time the way there is for Input Monitoring, so this reflects what actually happened rather
than a prediction).

### If auto-paste still doesn't work after granting Automation

This is a macOS code-identity issue, not merely a settings-checkbox problem. The short version:
macOS ties permission grants to a process's *code identity*, and a bare Python
interpreter run from a venv (ad-hoc signed, no stable Team ID, often several symlink hops
into a Homebrew Cellar path) can have an unstable identity — a grant that worked can
silently break after something as unrelated as `brew upgrade python@3.13`, and the
permission checkbox can appear checked while pointing at a stale/mismatched entry. If
you're stuck:

1. Confirm exactly which binary needs the grant:
   `source .venv/bin/activate && python3 -c "import sys, os; print(os.path.realpath(sys.executable))"`
   — that's the one file that needs to be checked in Automation/Input Monitoring, not
   "Python" or "Terminal" in the abstract.
2. Try `tccutil reset Automation` (or `tccutil reset Accessibility` if you're on the
   optional Fn backend, which still uses raw keystroke synthesis) to clear any stale
   entries, then fully quit and relaunch (not just re-toggle the checkbox — a running
   process can hold a stale in-memory permission state).
3. If it keeps regressing, the durable fix is packaging this as a minimal, stable-identity
   `.app` bundle (e.g. via `py2app` alias mode + ad-hoc `codesign`) instead of running from
   a raw venv interpreter — not done in this version, noted as a future improvement.

Whatever happens with permissions, the **HUD fallback always works** (see below) — you're
never stuck with an invisible, silent failure.

## Configuration

Tunable values live in `config.py` — no need to touch code elsewhere:

- `TRIGGER` — `"combo"` (default) or `"fn"`.
- `TRIGGER_KEY` / `TRIGGER_MODIFIERS` — only used when `TRIGGER = "combo"`. `TRIGGER_KEY`
  is any single letter/number key; `TRIGGER_MODIFIERS` is any subset of `{"control",
  "option", "command", "shift"}`. Default: `d` + `{control, option, command}`. Change these
  and restart the app to use a different combo — if you pick one that collides with an
  existing system/app shortcut, just try another.
- `AUTO_PASTE` — `True` (default) synthesizes ⌘V after transcribing; `False` copies to the
  clipboard only (no Accessibility permission needed).
- `MODEL` — the mlx-whisper model repo to use.
- `MAX_RECORDING_SECONDS` — safety cap for one recording; defaults to 300 seconds.
- `IDLE_TIMEOUT_MINUTES` — unload model memory after inactivity; set to `0` to disable.

While transcription is running the menu-bar icon shows an hourglass. If processing fails twice,
the recording is retained and the menu offers **Retry Failed Dictation** or **Discard Failed
Dictation**. The running process appears as `local-dictation` in Activity Monitor.
- Combo debounce (`COMBO_DEBOUNCE_SECONDS`), capture hardening (`MAX_RECORDING_SECONDS`),
  and hallucination/short-clip guard thresholds (`MIN_RECORDING_SECONDS`,
  `RMS_SILENCE_THRESHOLD`, `NO_SPEECH_PROB_THRESHOLD`, `AVG_LOGPROB_THRESHOLD`,
  `COMPRESSION_RATIO_THRESHOLD`) are all tunable if real-world use suggests different
  defaults.

### Optional: the Fn/Globe key backend

Set `TRIGGER = "fn"` in `config.py` to use a bare tap of the Fn/Globe key instead of a
combo (`FnTapTrigger` in `trigger.py`, still built and available, just no longer the
default — it required more complex bare-tap-vs-combo discrimination and coexists uneasily
with Apple's own Fn-dictation shortcut). If you use it, first disable macOS's own Fn/Globe
dictation shortcut so it doesn't race this app's toggle: **System Settings → Keyboard →
Dictation → Shortcut → Off**. `FN_TAP_HOLD_WINDOW_SECONDS` / `FN_TAP_DEBOUNCE_SECONDS` in
`config.py` tune its bare-tap detection.

## Architecture

The code is organized into `src/local_dictation/` with clear separation between pure logic
(`core/`) and OS integration (`adapters/`):

**Core modules (pure logic, no OS dependencies):**

| File | Responsibility |
|---|---|
| `core/filters.py` | `accept(audio, result)`: duration/energy/hallucination-confidence guards so silent or accidental toggles paste nothing |
| `core/transcriber.py` | Wraps `mlx_whisper.transcribe(...)`, returns the full result (text, language, per-segment confidence signals) |

**Adapter modules (OS-specific integration):**

| File | Responsibility |
|---|---|
| `adapters/trigger.py` | `ComboTrigger` (default: configurable modifier+key combo) and `FnTapTrigger` (optional: bare Fn tap), both pyobjc/Quartz `CGEventTap`-based with self-healing if macOS disables the tap; `create_trigger()` picks one based on `config.TRIGGER` |
| `adapters/recorder.py` | Opens the mic only for the duration of an active recording (never idle-active), with a max-duration auto-stop cap |
| `adapters/hotkey.py` | `DictationController`: owns the toggle → record → hand-off lifecycle (the trigger starts/stops recording; doesn't know how transcription happens) |
| `adapters/paste.py` | ⌘V synthesis via AppleScript/System Events and the focus-changed guard; leaves dictated text on the clipboard afterward (no restore — see below) |
| `adapters/hud.py` | A floating, permission-independent panel showing the transcribed text near the cursor whenever auto-paste doesn't land |

**Main modules:**

| File | Responsibility |
|---|---|
| `config.py` | All tunable constants; also sets `HF_HUB_DISABLE_PROGRESS_BARS` before mlx_whisper is imported anywhere |
| `worker.py` | Serialized transcription queue — `submit()` is thread-safe, `process_pending()` must run on one thread (the main thread, driven by `app.py`'s timer) — see below |
| `app.py` | Menu-bar app (`rumps`) wiring everything together, plus status and "Copy Last Dictation" |
| `cli.py` | Console script entry point for `local-dictation-dictate` command |

### Why transcription runs on the main thread

MLX's GPU stream is thread-local. During development, running transcription on a dedicated
background worker thread — even after explicitly registering a stream on that thread —
crashed with `There is no Stream(gpu, N) in current thread` (a known class of issue in
`ml-explore/mlx`). Every call made from the main thread, by contrast, has always worked
reliably. So `worker.py` keeps a thread-safe queue you can `submit()` to from any thread
(e.g. the trigger's own thread), but the actual transcription (`process_pending()`) must
always run on the same thread — in `app.py` that's the main thread, polled by a
`rumps.Timer`. This still gives serialized, in-order, non-blocking-recording behavior for
rapid consecutive dictations; it just means a transcription in progress briefly occupies
the main run loop (sub-second for the clip lengths this app handles).

### Why auto-paste goes through System Events instead of a raw keystroke API

The first version synthesized ⌘V directly via `Quartz.CGEventPost`, gated by the
Accessibility permission. In real use this permission kept failing even after repeated,
correct-looking grants — investigation traced it to TCC identity instability for a bare
venv Python interpreter (see the permissions section above). Routing the keystroke through AppleScript
(`osascript -e 'tell application "System Events" to keystroke ...'`) instead shifts the
permission requirement to Automation, checked by asking a first-party, permanently-stable
Apple process (System Events) to do the actual injection. This has two concrete
advantages: the Automation permission prompt reliably appears even for unbundled
interpreters (Accessibility's often doesn't), and `osascript`'s exit code actually tells
us whether the paste happened — `CGEventPost` posts an event and reports nothing back
either way.

### Why there's a HUD

No text-insertion mechanism on macOS — synthesized keystrokes, direct Accessibility-API
text insertion, AppleScript keystrokes — sidesteps needing *some* form of automation
permission; there's no bypass. So `hud.py` provides a fallback tier that needs none: a
small floating panel near your cursor showing the transcribed text for a couple of
seconds whenever auto-paste doesn't land, so grabbing it with a manual ⌘V is a
near-zero-friction next step instead of a silent, easy-to-miss clipboard write.

### Why auto-paste doesn't restore your previous clipboard

An earlier version copied the dictation to the clipboard, synthesized ⌘V, then restored
your previous clipboard contents after a short fixed delay. In real use this turned out to
be a genuine race condition: if the target app took longer than that delay to actually read
the pasteboard, the restore fired first and the app ended up reading the *restored* (stale)
content instead of the real dictation — there's no reliable OS-level signal for "the target
has now consumed the paste," so a fixed delay can never be made fully safe. Auto-paste now
simply leaves the dictated text on the clipboard afterward (like most dictation tools), and
a "Copy Last Dictation" menu item gives you a clipboard-independent way to recover the most
recent transcription at any time.

## Scope (v2)

- Batch transcription only (record fully, then transcribe) — no live streaming.
- One language per utterance — no mid-sentence English/German code-switching.
- The mic is only active during a recording; there's a small, unmitigated stream-startup
  latency at the very start of each recording as a result (a pre-roll buffer was tried and
  removed — it required keeping the mic continuously active, which is worse).
- No automatic clipboard restore (see above) — only plain text is ever placed on the
  clipboard, and it stays there after a dictation rather than being reverted.
- No packaging/signing — run from source in a venv.

### Explicitly deferred (not built in this change)

- **Silero VAD** gate/trim — the energy + duration + Whisper-confidence guards in
  `filters.py` are the v2 bar; VAD is the natural next step if hallucinations still occur
  in practice.
- A **hallucination-phrase blocklist** (exact-match backstop after the confidence gates).
- A **type-via-keystroke** or **Accessibility-API text insertion** paste fallback that
  would avoid the clipboard entirely (and with it, any residual paste-timing risk).
- Handling **audio device/sample-rate changes** mid-recording.
- A `mouse:<button>` trigger backend — `trigger.py`'s interface allows adding one later.
