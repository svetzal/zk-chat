from enum import StrEnum

from pydantic import BaseModel, Field


class MCPServerType(StrEnum):
    STDIO = "stdio"
    HTTP = "http"


class MCPServerConfig(BaseModel):
    name: str
    server_type: MCPServerType
    command: str | None = None
    url: str | None = None
    args: list[str] | None = Field(default_factory=list)

    def model_post_init(self, __context) -> None:
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
        self.bookmarks.add(vault_path)

    def remove_bookmark(self, vault_path: str) -> bool:
        if vault_path in self.bookmarks:
            self.bookmarks.remove(vault_path)
            # If we're removing the last opened bookmark, clear it
            if self.last_opened_bookmark == vault_path:
                self.last_opened_bookmark = None
            return True
        return False

    def get_bookmark(self, vault_path: str) -> str | None:
        return vault_path if vault_path in self.bookmarks else None

    def set_last_opened_bookmark(self, vault_path: str) -> bool:
        if vault_path in self.bookmarks:
            self.last_opened_bookmark = vault_path
            return True
        return False

    def get_last_opened_bookmark_path(self) -> str | None:
        if self.last_opened_bookmark and self.last_opened_bookmark in self.bookmarks:
            return self.last_opened_bookmark
        return None

    def add_mcp_server(self, server_config: MCPServerConfig) -> None:
        self.mcp_servers[server_config.name] = server_config

    def remove_mcp_server(self, server_name: str) -> bool:
        if server_name in self.mcp_servers:
            del self.mcp_servers[server_name]
            return True
        return False

    def get_mcp_server(self, server_name: str) -> MCPServerConfig | None:
        return self.mcp_servers.get(server_name)

    def list_mcp_servers(self) -> list[MCPServerConfig]:
        return list(self.mcp_servers.values())
