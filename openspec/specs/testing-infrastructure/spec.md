## Purpose

The project adopts pytest as its test framework with organized unit and integration tests, shared fixtures via conftest.py, and markers for slow tests. Tests are modern, readable, maintainable, and enable fast iteration (unit tests only) or full validation (with integration tests).

## Requirements

### Requirement: Test suite uses pytest instead of unittest
The project SHALL use pytest as its test runner. Tests MAY use unittest-compatible helpers where
they make macOS integration seams practical, but new tests SHOULD prefer plain pytest functions.

#### Scenario: Test files use pytest syntax
- **WHEN** a developer examines a test file (e.g., `tests/unit/test_config.py`)
- **THEN** it contains plain functions (`def test_*`) with `assert` statements, not unittest.TestCase subclasses or `self.assertX`

#### Scenario: Tests run via pytest command
- **WHEN** a developer runs `pytest tests/` in the project root
- **THEN** all tests are discovered and executed without error

#### Scenario: Individual test files run via pytest
- **WHEN** a developer runs `pytest tests/unit/test_config.py -v`
- **THEN** all test functions in that file are executed

### Requirement: Tests are organized into unit and integration directories
The project SHALL organize tests as `tests/unit/` for fast (mocked) tests and `tests/integration/` for slow (real model/audio) tests.

#### Scenario: Unit tests directory exists
- **WHEN** a developer lists the project structure
- **THEN** `tests/unit/` contains test files like `test_config.py`, `test_worker.py`, `test_filters.py`

#### Scenario: Integration tests directory exists
- **WHEN** a developer lists the project structure
- **THEN** `tests/integration/` contains test files like `test_idle_unload.py`, `test_hide_dock_icon.py`, `test_transcription_fixtures.py`

#### Scenario: Unit tests run quickly
- **WHEN** a developer runs `pytest tests/unit/ -v`
- **THEN** all tests complete in under 10 seconds (no real model loading)

### Requirement: conftest.py provides shared fixtures
The project SHALL have `tests/conftest.py` with reusable fixtures for mocking clipboard, rumps.App, and other common OS/UI dependencies.

#### Scenario: conftest.py exists at tests root
- **WHEN** a developer examines the project structure
- **THEN** `tests/conftest.py` exists and is importable by all unit and integration tests

#### Scenario: Fixtures are available to all test files
- **WHEN** a test function declares a fixture parameter (e.g., `def test_something(fake_clipboard)`)
- **THEN** pytest automatically injects the fixture from conftest.py without import statements

#### Scenario: Mock fixtures support common use cases
- **WHEN** a test needs to verify clipboard operations without touching the real clipboard
- **THEN** conftest.py provides a `fake_clipboard` fixture that captures clipboard.copy() calls

### Requirement: Integration tests are marked and can be skipped
The project SHALL use `@pytest.mark.integration` to mark slow tests (real model loading, audio fixtures) so they can be skipped during fast iteration.

#### Scenario: Integration tests are marked
- **WHEN** examining integration test files
- **THEN** each test function has a `@pytest.mark.integration` decorator

#### Scenario: Integration tests can be excluded from default run
- **WHEN** a developer runs `pytest tests/unit/`
- **THEN** only unit tests run; integration tests are not executed

#### Scenario: Integration tests can be included explicitly
- **WHEN** a developer runs `pytest -m integration`
- **THEN** all marked integration tests run (and real model loads, taking more time)

### Requirement: Test assertions are readable
The project SHALL use plain `assert` statements with clear conditions, avoiding nested conditionals or complex boolean logic that obscure test intent.

#### Scenario: Test assertions use simple comparisons
- **WHEN** examining a test file
- **THEN** assertions are written as `assert result == expected` or `assert value > 0`, not `self.assertTrue(expr)` or `self.assertEqual(...)`

#### Scenario: Test failure messages are clear
- **WHEN** a test fails and produces a traceback
- **THEN** the failure message clearly shows the expected vs. actual values (pytest's default `assert` introspection does this)

### Requirement: pyproject.toml declares pytest configuration
The project SHALL have `[tool.pytest.ini_options]` in `pyproject.toml` that sets test paths and slow-test markers.

#### Scenario: pytest is configured in pyproject.toml
- **WHEN** `pyproject.toml` is examined
- **THEN** it contains `[tool.pytest.ini_options]` with `testpaths = ["tests"]` and `markers = ["integration: slow tests requiring real model/audio fixtures"]`

#### Scenario: pytest discovers tests automatically
- **WHEN** a developer runs `pytest` in the project root
- **THEN** pytest discovers all test files in `tests/` without requiring explicit paths or arguments
