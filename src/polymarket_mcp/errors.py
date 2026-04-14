"""Structured error types for the Polymarket MCP package.

Purpose:
    Provide domain-specific exceptions and helpers for surfacing upstream API
    failures with clear, typed context.

Design:
    Errors are separated from transport and service code so upstream HTTP issues
    can be normalized once and handled consistently across the package.

Attributes:
    PolymarketError:
        Base package exception.
    UpstreamRequestError:
        Raised when a request to a Polymarket upstream service fails.
    UpstreamResponseError:
        Raised when a Polymarket upstream service returns malformed data.
"""

from __future__ import annotations

from http import HTTPStatus


class PolymarketError(Exception):
    """Base package exception.

    Args:
        message: Human-readable error description.

    Returns:
        None.

    Raises:
        None.
    """


class UpstreamRequestError(PolymarketError):
    """Raised when a Polymarket upstream request fails.

    Args:
        domain: Upstream API domain such as ``gamma`` or ``clob``.
        path: Relative request path.
        message: Human-readable error description.
        status_code: Optional upstream HTTP status code.

    Returns:
        None.

    Raises:
        None.
    """

    def __init__(
        self,
        *,
        domain: str,
        path: str,
        message: str,
        status_code: int | None = None,
    ) -> None:
        self.domain = domain
        self.path = path
        self.message = message
        self.status_code = status_code
        super().__init__(self.__str__())

    @property
    def status_name(self) -> str | None:
        """Return a symbolic HTTP status name when available.

        Args:
            None.

        Returns:
            str | None: Symbolic status name such as ``NOT_FOUND``.

        Raises:
            ValueError: If the status code is invalid.
        """
        if self.status_code is None:
            return None
        return HTTPStatus(self.status_code).name

    def __str__(self) -> str:
        """Render the exception as a compact message.

        Args:
            None.

        Returns:
            str: Human-readable error message.

        Raises:
            None.
        """
        status_fragment = (
            f" status={self.status_code}({self.status_name})"
            if self.status_code is not None
            else ""
        )
        return (
            f"Upstream request failed for domain={self.domain} path={self.path}."
            f"{status_fragment} message={self.message}"
        )


class UpstreamResponseError(PolymarketError):
    """Raised when an upstream response cannot be normalized safely.

    Args:
        domain: Upstream API domain such as ``gamma`` or ``data``.
        path: Relative request path.
        message: Human-readable error description.

    Returns:
        None.

    Raises:
        None.
    """

    def __init__(self, *, domain: str, path: str, message: str) -> None:
        self.domain = domain
        self.path = path
        self.message = message
        super().__init__(self.__str__())

    def __str__(self) -> str:
        """Render the exception as a compact message.

        Args:
            None.

        Returns:
            str: Human-readable error message.

        Raises:
            None.
        """
        return (
            f"Upstream response could not be normalized for domain={self.domain} "
            f"path={self.path}. message={self.message}"
        )
