## 1. Fix the release workflow

- [ ] 1.1 Change `release.yml`'s `release` job to `runs-on: macos-14`.

## 2. Correct the stale release-management spec

- [ ] 2.1 Rewrite the "Intentional local release" requirement to describe the automated,
      CI-triggered release process.
- [ ] 2.2 Correct the capability's `Purpose` in `openspec/specs/release-management/spec.md` directly.

## 3. Validation

- [ ] 3.1 `openspec validate --all --strict`, `ruff check .`, `pytest tests/unit -q`, `uv build` all
      pass.
- [ ] 3.2 After merge, confirm the next qualifying push runs `release.yml` to completion
      successfully on `macos-14`.
