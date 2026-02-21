from enum import StrEnum

from pydantic import BaseModel, Field


class MCPServerType(StrEnum):
    """Type of MCP server connection."""

    STDIO = "stdio"
    HTTP = "http"


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server."""

    name: str
    server_type: MCPServerType
    command: str | None = None
    url: str | None = None
    args: list[str] | None = Field(default_factory=list)

    def model_post_init(self, __context):
        if self.server_type == MCPServerType.STDIO and not self.command:
            raise ValueError("STDIO server requires a command")
        if self.server_type == MCPServerType.HTTP and not self.url:
            raise ValueError("HTTP server requires a URL")


class GlobalConfig(BaseModel):
    """
    Global configuration for zk_chat that persists across sessions.
    Stores bookmarks, the last opened bookmark, and registered MCP servers.

    This is a pure data model — all persistence is handled by GlobalConfigGateway.
    Path resolution (e.g. os.path.abspath) is the caller's responsibility.
    """

    bookmarks: set[str] = set()  # set of absolute vault paths
    last_opened_bookmark: str | None = None  # absolute path of the last opened bookmark
    mcp_servers: dict[str, MCPServerConfig] = Field(default_factory=dict)  # registered MCP servers by name

    def add_bookmark(self, vault_path: str) -> None:
        """Add a bookmark with the given vault path."""
        self.bookmarks.add(vault_path)

    def remove_bookmark(self, vault_path: str) -> bool:
        """Remove a bookmark with the given vault path. Returns True if successful."""
        if vault_path in self.bookmarks:
            self.bookmarks.remove(vault_path)
            # If we're removing the last opened bookmark, clear it
            if self.last_opened_bookmark == vault_path:
                self.last_opened_bookmark = None
            return True
        return False

    def get_bookmark(self, vault_path: str) -> str | None:
        """Get the bookmark path if it exists."""
        return vault_path if vault_path in self.bookmarks else None

    def set_last_opened_bookmark(self, vault_path: str) -> bool:
        """Set the last opened bookmark. Returns True if successful."""
        if vault_path in self.bookmarks:
            self.last_opened_bookmark = vault_path
            return True
        return False

    def get_last_opened_bookmark_path(self) -> str | None:
        """Get the path for the last opened bookmark."""
        if self.last_opened_bookmark and self.last_opened_bookmark in self.bookmarks:
            return self.last_opened_bookmark
        return None

    def add_mcp_server(self, server_config: MCPServerConfig) -> None:
        """Add or update an MCP server configuration."""
        self.mcp_servers[server_config.name] = server_config

    def remove_mcp_server(self, server_name: str) -> bool:
        """Remove an MCP server configuration. Returns True if successful."""
        if server_name in self.mcp_servers:
            del self.mcp_servers[server_name]
            return True
        return False

    def get_mcp_server(self, server_name: str) -> MCPServerConfig | None:
        """Get an MCP server configuration by name."""
        return self.mcp_servers.get(server_name)

    def list_mcp_servers(self) -> list[MCPServerConfig]:
        """List all registered MCP servers."""
        return list(self.mcp_servers.values())
