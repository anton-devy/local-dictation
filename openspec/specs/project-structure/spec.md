## Purpose

The project adopts standard Python packaging conventions: src-layout (`src/local_dictation/`) with organized subdirectories (core for pure logic, adapters for OS integration), proper `pyproject.toml` with dependency management, and package-relative imports. Code becomes relocatable, installable, and maintainable as a real Python package.

## Requirements

### Requirement: Project uses src-layout structure
The project SHALL organize code as `src/local_dictation/` with subdirectories for `core/` (pure logic) and `adapters/` (OS integration).

#### Scenario: Core directory contains pure logic modules
- **WHEN** a developer examines the project structure
- **THEN** `src/local_dictation/core/` contains `filters.py` and `transcriber.py` with no imports of AppKit, rumps, sounddevice, or OS-specific libraries

#### Scenario: Adapters directory contains OS integration modules
- **WHEN** a developer examines the project structure
- **THEN** `src/local_dictation/adapters/` contains `hotkey.py`, `hud.py`, `paste.py`, `recorder.py`, and `trigger.py` (all OS-specific integration)

#### Scenario: App composition root is at package level
- **WHEN** a developer looks for the main app entry point
- **THEN** `src/local_dictation/app.py` exists as the rumps.App composition root

### Requirement: Project has pyproject.toml with hatchling backend
The project SHALL declare build system, dependencies, and entry points in `pyproject.toml` using hatchling as the build backend.

#### Scenario: pyproject.toml declares dependencies
- **WHEN** the project's `pyproject.toml` is read
- **THEN** it contains a `[project]` table with `dependencies` list including mlx-whisper, sounddevice, rumps, pyperclip, pyobjc-framework-Quartz, pyobjc-framework-Cocoa

#### Scenario: pyproject.toml declares build system
- **WHEN** the project's `pyproject.toml` is read
- **THEN** it contains `[build-system]` with `requires = ["hatchling"]` and `build-backend = "hatchling.build"`

#### Scenario: pyproject.toml defines console scripts
- **WHEN** the project is installed via `pip install -e .`
- **THEN** the `local-dictation` command becomes available, pointing to `local_dictation.app:main`

### Requirement: All imports use package-relative style
The project SHALL use `from local_dictation import config` (absolute from package root) and `from . import <module>` (relative within subpackages). No flat imports like `import config`.

#### Scenario: Imports work from anywhere in the package
- **WHEN** code in `src/local_dictation/adapters/hotkey.py` needs to import config
- **THEN** it uses `from local_dictation import config`, not `import config`

#### Scenario: Relative imports work within subpackages
- **WHEN** code in `src/local_dictation/core/transcriber.py` needs to import from core
- **THEN** it uses `from . import filters`, not `from core import filters` or `import filters`

### Requirement: Project is installable as a package
The project SHALL be installable via `pip install -e .` without errors, allowing the app to run as `local-dictation` command or `python -m local_dictation.app`.

#### Scenario: pip install -e succeeds
- **WHEN** a developer runs `pip install -e .` in the project root
- **THEN** the command completes without error

#### Scenario: local-dictation command runs the app
- **WHEN** a developer runs `local-dictation` after installation
- **THEN** the app launches normally (menu-bar icon appears, hotkey is active)

#### Scenario: python -m invocation works
- **WHEN** a developer runs `python -m local_dictation.app`
- **THEN** the app launches normally

### Requirement: Fixtures directory exists and is accessible
The project SHALL keep audio fixtures in `fixtures/` and make them accessible to integration tests via relative paths that work from the installed package.

#### Scenario: Fixture files are present
- **WHEN** a test needs to load a fixture audio file
- **THEN** files like `fixtures/sample-english.wav` exist and can be opened

#### Scenario: Fixture paths resolve correctly in tests
- **WHEN** an integration test runs
- **THEN** fixture paths resolve relative to the project root or via importlib.resources (not relative to the test file)
