## 1. Compact and correct the README

- [x] 1.1 Rewrite the Install section to lead with `uv sync` (matching `AGENTS.md`/`ci.yml`), keeping
      venv + `pip install -e .` as a fallback.
- [x] 1.2 Fix the three factual defects: the hotkey-modifier default (`README.md:140`), the Fn-backend
      keystroke claim (`README.md:123`), and the Activity Monitor claim (`README.md:151`).
- [x] 1.3 Repair the Configuration section's broken bullet list (`README.md:149-152`) and fold the
      stranded menu-item/status-line content into `## Usage`.
- [x] 1.4 Replace `## Scope (v2)` with `## Limitations`, keeping only the current-behavior bullets;
      remove the "Explicitly deferred" roadmap list.
- [x] 1.5 Remove the Architecture module tables and the four `### Why ...` postmortem sections; repair
      every cross-reference ("see below"/"see above") that pointed into them.
- [x] 1.6 Add a short `## Contributing` pointer to `CONTRIBUTING.md`/`AGENTS.md`.

## 2. Correct the drifted spec

- [x] 2.1 Narrow `menu-bar-app`'s "Descriptive process identity" requirement to process-/`ps`-level
      identity, preserving the requirement name exactly.

## 3. Validation

- [x] 3.1 `openspec validate --all --strict`, `ruff check .`, `pytest tests/unit -q`, `uv build` all
      pass.
- [x] 3.2 Confirm no documentation obligation (Input Monitoring, Automation, release dry-run command)
      was lost, and `README.md` is roughly 100 lines, down from 267.
