from enum import StrEnum

from pydantic import BaseModel, Field


class MCPServerType(StrEnum):
    """Transport type for a registered MCP server (STDIO process or HTTP endpoint)."""

    STDIO = "stdio"
    HTTP = "http"


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server entry stored in GlobalConfig."""

    name: str
    server_type: MCPServerType
    command: str | None = None
    url: str | None = None
    args: list[str] | None = Field(default_factory=list)

    def model_post_init(self, __context) -> None:
        """Validate that the required transport field is present after construction.

        Raises
        ------
        ValueError
            If ``server_type`` is STDIO and ``command`` is not set, or ``server_type``
            is HTTP and ``url`` is not set.
        """
        if self.server_type == MCPServerType.STDIO and not self.command:
            raise ValueError("STDIO server requires a command")
        if self.server_type == MCPServerType.HTTP and not self.url:
            raise ValueError("HTTP server requires a URL")


class GlobalConfig(BaseModel):
    """
    Global configuration for zk_chat that persists across sessions.
    Stores bookmarks, the last opened bookmark, and registered MCP servers.

    This is a pure data model — all persistence is handled by GlobalConfigGateway.
    Callers must pass paths produced by zk_chat.vault_path.normalize_vault_path so
    that every stored path is a canonical, symlink-resolved absolute path.
    """

    bookmarks: set[str] = set()  # set of canonical, symlink-resolved vault paths
    last_opened_bookmark: str | None = None  # canonical, symlink-resolved path of the last opened bookmark
    mcp_servers: dict[str, MCPServerConfig] = Field(default_factory=dict)  # registered MCP servers by name

    def add_bookmark(self, vault_path: str) -> None:
        """Add a vault path to the bookmark set (idempotent)."""
        self.bookmarks.add(vault_path)

    def remove_bookmark(self, vault_path: str) -> bool:
        """Remove a bookmark and clear ``last_opened_bookmark`` if it matched.

        Returns
        -------
        bool
            ``True`` if the bookmark existed and was removed, ``False`` if not found.
        """
        if vault_path in self.bookmarks:
            self.bookmarks.remove(vault_path)
            # If we're removing the last opened bookmark, clear it
            if self.last_opened_bookmark == vault_path:
                self.last_opened_bookmark = None
            return True
        return False

    def get_bookmark(self, vault_path: str) -> str | None:
        """Return ``vault_path`` if it is bookmarked, otherwise ``None``."""
        return vault_path if vault_path in self.bookmarks else None

    def set_last_opened_bookmark(self, vault_path: str) -> bool:
        """Set the last-opened bookmark, but only if the path is already bookmarked.

        Returns
        -------
        bool
            ``True`` if the bookmark existed and was set, ``False`` if not found.
        """
        if vault_path in self.bookmarks:
            self.last_opened_bookmark = vault_path
            return True
        return False

    def get_last_opened_bookmark_path(self) -> str | None:
        """Return the last-opened bookmark path, or ``None`` if unset or stale."""
        if self.last_opened_bookmark and self.last_opened_bookmark in self.bookmarks:
            return self.last_opened_bookmark
        return None

    def add_mcp_server(self, server_config: MCPServerConfig) -> None:
        """Register an MCP server, replacing any existing entry with the same name."""
        self.mcp_servers[server_config.name] = server_config

    def remove_mcp_server(self, server_name: str) -> bool:
        """Remove a registered MCP server by name.

        Returns
        -------
        bool
            ``True`` if the server existed and was removed, ``False`` if not found.
        """
        if server_name in self.mcp_servers:
            del self.mcp_servers[server_name]
            return True
        return False

    def get_mcp_server(self, server_name: str) -> MCPServerConfig | None:
        """Return the ``MCPServerConfig`` for the given name, or ``None`` if not registered."""
        return self.mcp_servers.get(server_name)

    def list_mcp_servers(self) -> list[MCPServerConfig]:
        """Return all registered MCP server configs as a list."""
        return list(self.mcp_servers.values())
