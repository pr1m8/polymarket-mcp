"""Environment-backed application settings for the Polymarket MCP package.

Purpose:
    Centralize configuration for the Polymarket MCP package using
    ``pydantic-settings`` so values can be provided through environment
    variables without custom parsing code.

Design:
    Settings are cached through :func:`load_settings` and loaded from the
    ``POLYMARKET_MCP_`` environment namespace.

Attributes:
    AppSettings:
        Root settings model.
    load_settings:
        Cached settings loader.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Typed application settings.

    Args:
        gamma_base_url: Base URL for the Gamma API.
        data_base_url: Base URL for the Data API.
        clob_base_url: Base URL for the CLOB API.
        request_timeout_seconds: Per-request timeout.
        enable_resources_as_tools: Whether to expose resources as generated
            tools.
        user_agent: Optional shared user-agent string for outbound requests.

    Returns:
        AppSettings: Validated settings object.

    Raises:
        ValueError: If any field fails validation.

    Examples:
        >>> settings = AppSettings()
        >>> settings.gamma_base_url
        'https://gamma-api.polymarket.com'
    """

    model_config = SettingsConfigDict(
        env_prefix="POLYMARKET_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    gamma_base_url: str = "https://gamma-api.polymarket.com"
    data_base_url: str = "https://data-api.polymarket.com"
    clob_base_url: str = "https://clob.polymarket.com"
    request_timeout_seconds: float = Field(default=20.0, gt=0)
    enable_resources_as_tools: bool = True
    user_agent: str = "polymarket-mcp/0.1.1"


@lru_cache(maxsize=1)
def load_settings() -> AppSettings:
    """Load and cache application settings.

    Args:
        None.

    Returns:
        AppSettings: Cached settings object.

    Raises:
        None.

    Examples:
        >>> settings = load_settings()
        >>> settings.enable_resources_as_tools in {True, False}
        True
    """
    return AppSettings()
