## 1. Bundle build

- [ ] 1.1 Add `setup.py` (repo root): py2app alias-mode config, `CFBundleIdentifier =
      com.devant0n.local-dictation`, `LSUIElement = True`, mic/AppleEvents usage descriptions.
- [ ] 1.2 Add `scripts/build_app.sh`: builds via `setup.py py2app -A` into `dist/`, ad-hoc signs with
      the fixed identifier, fails loudly on any step error.
- [ ] 1.3 Add a `bundle` optional-dependency group (`py2app`) to `pyproject.toml`, separate from
      `dev`.
- [ ] 1.4 Add `build/` to `.gitignore`.

## 2. Documentation

- [ ] 2.1 README `## Install`: document `./scripts/build_app.sh` as the supported way to get a
      runnable app; keep `uv sync` for development/testing.
- [ ] 2.2 README `## Usage`: note the bundle as the supported launch method; console script /
      `python -m local_dictation.app` reframed as development-only.
- [ ] 2.3 README `## Permissions (macOS)`: add the one-time permission-migration note — the three TCC
      grants must be re-granted against the bundle's new identity the first time it runs.

## 3. Spec alignment

- [ ] 3.1 `menu-bar-app`: ADD requirement `App bundle build`.
- [ ] 3.2 `menu-bar-app`: MODIFY requirement `Descriptive process identity` (name preserved exactly)
      to assert the bundle's Activity Monitor name, with a separate console-script scenario.
- [ ] 3.3 `release-management`: MODIFY requirement `Intentional local release` to scope the
      no-app-bundle prohibition to the CI release process.

## 4. Validation

- [ ] 4.1 `openspec validate --all --strict`, `ruff check .`, `pytest tests/unit -q`, `uv build` all
      pass.
- [ ] 4.2 `./scripts/build_app.sh` produces `dist/local-dictation.app`; `ps -Ao ucomm` on the running
      bundle reports `local-dictation`.
- [ ] 4.3 Human confirms once: Input Monitoring + Automation grants against the new bundle identity,
      a real hotkey → transcribe → paste round-trip, and that the grant survives one rebuild+re-sign.
