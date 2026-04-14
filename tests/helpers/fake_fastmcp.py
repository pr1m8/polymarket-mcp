"""FastMCP test doubles used by the Polymarket MCP test suite.

Purpose:
    Provide a tiny fake ``fastmcp`` implementation so tests can import the
    package without installing the runtime dependency.

Design:
    The fake module mirrors only the small subset of behavior needed by the
    current tests: server construction, mounting, transforms, and decorator
    registration.
"""

from __future__ import annotations

import sys
import types


class FakeFastMCP:
    """Tiny FastMCP test double used for server composition tests.

    Args:
        name: Server name.
        instructions: Optional server instructions.
        strict_input_validation: Optional validation flag.
        mask_error_details: Optional masking flag.

    Returns:
        FakeFastMCP: Configured fake server.

    Raises:
        None.
    """

    def __init__(
        self,
        name: str,
        instructions: str | None = None,
        strict_input_validation: bool | None = None,
        mask_error_details: bool | None = None,
    ) -> None:
        self.name = name
        self.instructions = instructions
        self.strict_input_validation = strict_input_validation
        self.mask_error_details = mask_error_details
        self.mounts: list[tuple[str | None, object]] = []
        self.transforms: list[object] = []
        self.registered_tools: list[tuple[str, object]] = []
        self.registered_resources: list[tuple[str, str, object]] = []
        self.registered_prompts: list[tuple[str, object]] = []

    def mount(self, server: object, prefix: str | None = None, namespace: str | None = None) -> None:
        """Record a mounted child server.

        Args:
            server: Mounted child server.
            prefix: Optional mount prefix.
            namespace: Optional mount namespace.

        Returns:
            None.

        Raises:
            None.
        """
        self.mounts.append((prefix or namespace, server))

    def add_transform(self, transform: object) -> None:
        """Record an added transform.

        Args:
            transform: Added transform object.

        Returns:
            None.

        Raises:
            None.
        """
        self.transforms.append(transform)

    def tool(self, fn: object | None = None, *, name: str | None = None):
        """Register a tool using decorator or direct-call style."""
        def decorator(inner: object) -> object:
            self.registered_tools.append((name or getattr(inner, "__name__", "tool"), inner))
            return inner

        if fn is None:
            return decorator
        return decorator(fn)

    def resource(self, uri_template: str, name: str | None = None):
        """Register a resource using decorator style."""
        def decorator(inner: object) -> object:
            self.registered_resources.append((uri_template, name or getattr(inner, "__name__", "resource"), inner))
            return inner

        return decorator

    def prompt(self, fn: object | None = None, *, name: str | None = None):
        """Register a prompt using decorator or direct-call style."""
        def decorator(inner: object) -> object:
            self.registered_prompts.append((name or getattr(inner, "__name__", "prompt"), inner))
            return inner

        if fn is None:
            return decorator
        return decorator(fn)

    def run(self) -> None:
        """Provide a no-op run method for API parity.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        return None


class FakeResourcesAsTools:
    """Simple transform placeholder used in tests.

    Args:
        server: The fake server receiving the transform.

    Returns:
        FakeResourcesAsTools: Stored transform object.

    Raises:
        None.
    """

    def __init__(self, server: object) -> None:
        self.server = server


def build_fake_fastmcp_modules() -> dict[str, types.ModuleType]:
    """Build fake ``fastmcp`` modules for tests.

    Args:
        None.

    Returns:
        dict[str, types.ModuleType]: Fake modules keyed by import path.

    Raises:
        None.
    """
    fastmcp_module = types.ModuleType("fastmcp")
    fastmcp_module.FastMCP = FakeFastMCP
    server_module = types.ModuleType("fastmcp.server")
    transforms_module = types.ModuleType("fastmcp.server.transforms")
    transforms_module.ResourcesAsTools = FakeResourcesAsTools
    return {
        "fastmcp": fastmcp_module,
        "fastmcp.server": server_module,
        "fastmcp.server.transforms": transforms_module,
    }


def install_fake_fastmcp(*, force: bool = False) -> types.ModuleType:
    """Install fake ``fastmcp`` modules into ``sys.modules``.

    Args:
        force: Replace any existing ``fastmcp`` modules when ``True``.

    Returns:
        types.ModuleType: Injected root fake ``fastmcp`` module.

    Raises:
        None.
    """
    modules = build_fake_fastmcp_modules()
    for module_name, module in modules.items():
        if force or module_name not in sys.modules:
            sys.modules[module_name] = module
    return sys.modules["fastmcp"]
