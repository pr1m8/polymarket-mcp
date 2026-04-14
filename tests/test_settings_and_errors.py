"""Tests for environment-backed settings and structured error helpers."""

from __future__ import annotations

from polymarket_mcp.errors import UpstreamRequestError
from polymarket_mcp.settings import AppSettings, load_settings


def test_app_settings_reads_environment_prefix(monkeypatch) -> None:
    """Environment-prefixed values should override defaults."""
    monkeypatch.setenv("POLYMARKET_MCP_REQUEST_TIMEOUT_SECONDS", "7.5")
    monkeypatch.setenv("POLYMARKET_MCP_ENABLE_RESOURCES_AS_TOOLS", "false")

    settings = AppSettings()

    assert settings.request_timeout_seconds == 7.5
    assert settings.enable_resources_as_tools is False


def test_load_settings_is_cached() -> None:
    """The cached settings loader should return the same object instance."""
    load_settings.cache_clear()
    first = load_settings()
    second = load_settings()

    assert first is second


def test_upstream_request_error_includes_status_name() -> None:
    """Structured upstream errors should include symbolic HTTP status names."""
    error = UpstreamRequestError(
        domain="gamma",
        path="/markets",
        message="not found",
        status_code=404,
    )

    assert error.status_name == "NOT_FOUND"
    assert "domain=gamma" in str(error)
    assert "404(NOT_FOUND)" in str(error)
