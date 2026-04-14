"""Shared HTTP utilities for Polymarket API access.

Purpose:
    Provide a small async HTTP adapter shared by service modules.

Design:
    The adapter returns parsed JSON and maps transport and HTTP failures into
    package-specific exceptions so upstream failures are easier to diagnose and
    test.

Attributes:
    JsonHttpClient:
        Shared async JSON HTTP client.
"""

from __future__ import annotations

from typing import Any

import httpx

from polymarket_mcp.errors import UpstreamRequestError


class JsonHttpClient:
    """Minimal async JSON client.

    Args:
        base_url: Base URL for requests.
        timeout: Request timeout in seconds.
        domain: Logical API domain name.
        user_agent: Shared outbound user-agent string.

    Returns:
        JsonHttpClient: Configured HTTP adapter.

    Raises:
        None.
    """

    def __init__(
        self,
        *,
        base_url: str,
        timeout: float,
        domain: str,
        user_agent: str,
    ) -> None:
        self._base_url = base_url
        self._timeout = timeout
        self._domain = domain
        self._headers = {"User-Agent": user_agent}

    async def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Issue a GET request and parse JSON.

        Args:
            path: Relative API path.
            params: Optional query parameters.

        Returns:
            Any: Parsed JSON body.

        Raises:
            UpstreamRequestError: If the request fails.
        """
        async with httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            headers=self._headers,
        ) as client:
            try:
                response = await client.get(path, params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise UpstreamRequestError(
                    domain=self._domain,
                    path=path,
                    message=str(exc),
                    status_code=exc.response.status_code,
                ) from exc
            except httpx.HTTPError as exc:
                raise UpstreamRequestError(
                    domain=self._domain,
                    path=path,
                    message=str(exc),
                ) from exc
            return response.json()

    async def post(
        self,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        """Issue a POST request and parse JSON.

        Args:
            path: Relative API path.
            json_body: Optional JSON request body.

        Returns:
            Any: Parsed JSON body.

        Raises:
            UpstreamRequestError: If the request fails.
        """
        async with httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            headers=self._headers,
        ) as client:
            try:
                response = await client.post(path, json=json_body)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise UpstreamRequestError(
                    domain=self._domain,
                    path=path,
                    message=str(exc),
                    status_code=exc.response.status_code,
                ) from exc
            except httpx.HTTPError as exc:
                raise UpstreamRequestError(
                    domain=self._domain,
                    path=path,
                    message=str(exc),
                ) from exc
            return response.json()
