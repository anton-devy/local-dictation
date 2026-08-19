#!/usr/bin/env bash
# Build a local-dictation.app bundle in py2app alias mode and ad-hoc sign it with a stable
# identifier. Referencing the active environment, not vendoring anything -- see setup.py.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

BUNDLE_ID="com.devant0n.local-dictation"
APP_PATH="dist/local-dictation.app"

if ! uv run --extra bundle python -c "import py2app" >/dev/null 2>&1; then
    echo "error: py2app not available; run 'uv sync --extra bundle' first" >&2
    exit 1
fi

rm -rf build "$APP_PATH"

uv run --extra bundle python setup.py py2app -A

codesign --sign - --force --deep --identifier "$BUNDLE_ID" "$APP_PATH"

echo "Built and signed: $REPO_ROOT/$APP_PATH"
