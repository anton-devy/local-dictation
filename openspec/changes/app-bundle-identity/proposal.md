## Why

`ps -o ucomm` — what Activity Monitor's Process Name column reads — reports the running app as
`Python`, not `local-dictation`. The console-script launch chain re-execs into Homebrew's
`Python.framework/.../Python.app/Contents/MacOS/Python`; the kernel's `p_comm` reflects that exec'd
binary, not `setproctitle`'s argv rewrite (`app.py:293`, which correctly sets `ps -o comm` and stays
unchanged). A symlink cannot fix this — macOS resolves symlinks before setting `p_comm`.

Not purely cosmetic: because the process *is* Homebrew's `Python.app`, every TCC grant (Input
Monitoring, Automation, Microphone) is scoped to Homebrew Python globally and can be invalidated by
an unrelated `brew upgrade python@3.13` — the instability `paste.py`'s docstring and the README's TCC
section already document. A bundle with a stable, signed identity fixes both at once.

Spiked outside the repo first: py2app 0.28.10 alias mode, referencing the real venv (nothing
vendored), produces a bundle whose `ucomm` is `local-dictation`, boots cleanly, keeps accessory
activation policy, and runs real mlx-whisper inference correctly. Full detail in issue #18.

## What Changes

- New `setup.py` (repo root) — py2app alias-mode configuration only; hatchling remains the packaging
  backend for `pyproject.toml` per `project-structure`, unaffected by this change.
- New `scripts/build_app.sh` — one-command build + ad-hoc sign with a stable
  `com.devant0n.local-dictation` bundle identifier, so the identifier can never drift by hand.
- New `bundle` optional-dependency group in `pyproject.toml` (`py2app`), kept separate from `dev`
  (lint/test tooling).
- `.gitignore` gains `build/` — py2app writes both `build/` and `dist/`; `dist/` is already ignored.
- README: bundle build documented in `## Install` as the supported way to run the app; the console
  script reframed as the development path; a permission-migration note added to
  `## Permissions (macOS)` — the three TCC grants must be re-granted once, against the bundle's new
  identity.
- **ADDED** `menu-bar-app` requirement: `App bundle build` — the bundle SHALL build via the committed
  script and carry a stable, ad-hoc-signed identifier.
- **MODIFIED** `menu-bar-app` requirement: `Descriptive process identity` — replaces the current
  "Activity Monitor may still show the interpreter" escape hatch with an assertion that the *bundle*
  reports `local-dictation` to Activity Monitor, plus a separate scenario for the console-script
  path's own (unchanged) `ps` behavior, now framed as development-only.
- **MODIFIED** `release-management` requirement: `Intentional local release` — clarifies that "SHALL
  NOT... produce an app bundle" scopes the prohibition to the automated CI release process; a
  developer building a bundle locally, on demand, is explicitly permitted and unaffected.

## Impact

- Affected capabilities: `menu-bar-app` (one requirement added, one modified), `release-management`
  (one requirement modified).
- Affected files: `setup.py` (new), `scripts/build_app.sh` (new), `pyproject.toml` (new optional
  dependency group), `.gitignore`, `README.md`.
- No changes to `src/local_dictation/`: `setproctitle` stays in `app.py` — it remains correct for the
  console-script path, whose behavior is unchanged, only re-scoped as dev-only in documentation.
- Out of scope: a full py2app/PyInstaller freeze (vendoring mlx/Metal, PortAudio, numba — would
  contradict the source-only release policy), notarization/Developer ID signing, an app icon (no
  `.icns` exists yet), CI producing a bundle, HUD removal (separately deferred).
