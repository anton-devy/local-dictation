"""Optional local build for a macOS `.app` bundle in py2app *alias* mode.

Not the package's build system -- `pyproject.toml` + hatchling remain that, per the
`project-structure` spec. This file exists solely so `scripts/build_app.sh` can produce a
`local-dictation.app` that references the active environment (nothing vendored or frozen) and
carries a stable, ad-hoc-signed bundle identity, so macOS tools that read process/bundle identity
(Activity Monitor, TCC) see `local-dictation` instead of the underlying Python interpreter.
"""

import tempfile
import tomllib
from pathlib import Path

from setuptools import setup

APP = ["src/local_dictation/app.py"]

VERSION = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]

OPTIONS = {
    "argv_emulation": False,
    "alias": True,
    "plist": {
        "CFBundleName": "local-dictation",
        "CFBundleDisplayName": "local-dictation",
        "CFBundleIdentifier": "com.devant0n.local-dictation",
        "CFBundleShortVersionString": VERSION,
        "CFBundleVersion": VERSION,
        "LSUIElement": True,
        "NSMicrophoneUsageDescription": "local-dictation needs microphone access to record dictation.",
        "NSAppleEventsUsageDescription": "local-dictation uses System Events to auto-paste transcribed text.",
    },
}

setup(
    app=APP,
    name="local-dictation",
    # Keep setuptools from auto-merging pyproject.toml's [project] table (hatchling-owned, lists
    # runtime deps as install_requires) -- py2app alias mode refuses to run if install_requires is
    # set, since alias mode installs nothing, it only references the active environment.
    src_root=tempfile.mkdtemp(),
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
