"""Tests for idle-unload configuration."""

from local_dictation import config


def test_idle_timeout_configured():
    """IDLE_TIMEOUT_MINUTES should be configured."""
    assert hasattr(config, 'IDLE_TIMEOUT_MINUTES')


def test_idle_timeout_is_positive():
    """IDLE_TIMEOUT_MINUTES should be a positive number or zero."""
    assert isinstance(config.IDLE_TIMEOUT_MINUTES, int)
    assert config.IDLE_TIMEOUT_MINUTES >= 0


def test_default_idle_timeout_reasonable():
    """Default idle timeout should be reasonable (between 1-60 minutes)."""
    if config.IDLE_TIMEOUT_MINUTES > 0:
        assert config.IDLE_TIMEOUT_MINUTES <= 60


def test_idle_timeout_default_is_10_minutes():
    """Default idle timeout should be 10 minutes."""
    assert config.IDLE_TIMEOUT_MINUTES == 10


def test_model_is_configured():
    """MODEL should be configured."""
    assert hasattr(config, 'MODEL')
    assert isinstance(config.MODEL, str)
    assert len(config.MODEL) > 0
