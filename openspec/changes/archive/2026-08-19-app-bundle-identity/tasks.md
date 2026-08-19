## 1. Bundle build

- [x] 1.1 Add `setup.py` (repo root): py2app alias-mode config, `CFBundleIdentifier =
      com.devant0n.local-dictation`, `LSUIElement = True`, mic/AppleEvents usage descriptions.
- [x] 1.2 Add `scripts/build_app.sh`: builds via `setup.py py2app -A` into `dist/`, ad-hoc signs with
      the fixed identifier, fails loudly on any step error.
- [x] 1.3 Add a `bundle` optional-dependency group (`py2app`) to `pyproject.toml`, separate from
      `dev`.
- [x] 1.4 Add `build/` to `.gitignore`.

## 2. Documentation

- [x] 2.1 README `## Install`: document `./scripts/build_app.sh` as the supported way to get a
      runnable app; keep `uv sync` for development/testing.
- [x] 2.2 README `## Usage`: note the bundle as the supported launch method; console script /
      `python -m local_dictation.app` reframed as development-only.
- [x] 2.3 README `## Permissions (macOS)`: add the one-time permission-migration note — the three TCC
      grants must be re-granted against the bundle's new identity the first time it runs.

## 3. Spec alignment

- [x] 3.1 `menu-bar-app`: ADD requirement `App bundle build`.
- [x] 3.2 `menu-bar-app`: MODIFY requirement `Descriptive process identity` (name preserved exactly)
      to assert the bundle's Activity Monitor name, with a separate console-script scenario.
- [x] 3.3 `release-management`: MODIFY requirement `Intentional local release` to scope the
      no-app-bundle prohibition to the CI release process.

## 4. Validation

- [x] 4.1 `openspec validate --all --strict`, `ruff check .`, `pytest tests/unit -q`, `uv build` all
      pass.
- [x] 4.2 `./scripts/build_app.sh` produces `dist/local-dictation.app`; `ps -Ao ucomm` on the running
      bundle reports `local-dictation`. Also confirmed `menu-bar-only-activation` still holds
      (System Events: `backgroundOnly=true, visible=false`).
- [x] 4.3 Human-confirmed: Input Monitoring and Automation granted against the bundle identity, a
      real hotkey → transcribe → paste round-trip succeeded. Grant did **not** survive a rebuild
      (confirmed twice) — a documented limitation (README, spec), not a defect; see commit
      documenting it. Also surfaced and fixed an unrelated real bug along the way (#20:
      `UnicodeDecodeError` crash masking a permission failure).
