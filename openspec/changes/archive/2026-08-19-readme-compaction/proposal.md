## Why

`README.md` is 267 lines and carries ~75% of the project's human-facing prose, but its only hard
documentation obligations — Input Monitoring, Automation, the release dry-run command, and not
contradicting shipped behavior (per `openspec/specs/*`, `AGENTS.md`, `CONTRIBUTING.md`, and the PR
template) — need roughly 60-80 lines. The remainder mixes content duplicated from openspec,
engineering postmortems, and a stale "v2" scope label that conflates current limitations with genuine
future roadmap.

Three factual defects were found and verified against source while auditing the file for
compaction, not merely inferred:

- `README.md:140` states the default hotkey combo as `d` + `{control, option, command}`;
  `config.py:55` is actually `{"control", "shift"}` — and `README.md:6` already says
  Control+Shift+D, so the file contradicts itself 134 lines apart.
- `README.md:123` claims the optional Fn trigger backend "still uses raw keystroke synthesis"; the
  Fn backend only changes how the toggle is triggered — paste always goes through
  `_synthesize_cmd_v_osascript()` (`paste.py:94`) regardless of `TRIGGER`.
- `README.md:151` claims the process "appears as `local-dictation` in Activity Monitor". Verified
  false against the running app: `ps -o comm` shows `local-dictation` (argv, rewritten by
  `setproctitle.setproctitle()` at `app.py:293`), but `ps -o ucomm` (the kernel `p_comm` value
  Activity Monitor actually reads) shows `Python`, because the exec'd binary is Homebrew's
  `Python.framework/.../Python.app/Contents/MacOS/Python`. `setproctitle` works exactly as designed;
  it cannot change what Activity Monitor displays, because that reads the identity of the exec'd
  binary, not the rewritten argv.

`openspec/specs/menu-bar-app/spec.md`'s "Descriptive process identity" requirement makes the same
false Activity-Monitor claim, so it drifts from reality the same way the README does and needs
correcting alongside it.

## What Changes

- `README.md` compacted to roughly 100 lines: install rewritten to lead with `uv sync` (matching
  `AGENTS.md` and `ci.yml`, which the current `pip install -e .`-only instructions contradict), the
  three factual defects fixed, the broken Configuration list repaired, `## Scope (v2)` split into a
  renamed `## Limitations` (current-behavior bullets kept) with the genuine roadmap list removed, and
  the Architecture tables and four `### Why ...` engineering-postmortem sections removed outright
  (recoverable from git history and `openspec/changes/archive/`; no spec requires the README to carry
  them).
- **MODIFIED** `menu-bar-app` capability: "Descriptive process identity" requirement narrowed from an
  Activity-Monitor claim to the process-/`ps`-level identity `setproctitle` actually delivers.

## Impact

- Affected capability: `menu-bar-app` (one requirement modified).
- Affected file: `README.md` (content only — no code, dependency, or behavior change).
- Out of scope: HUD removal (deferred to a separate decision) and any `.app`-bundle packaging work —
  this only corrects the documentation/spec claim to match verified current behavior, without
  pursuing or foreclosing bundling.
