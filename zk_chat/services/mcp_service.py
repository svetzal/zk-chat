"""Service layer for MCP server management."""

from zk_chat.global_config import MCPServerConfig, MCPServerType
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.mcp_client import verify_mcp_server


class MCPValidationError(Exception):
    pass


class MCPService:
    """Manages MCP server registration, removal, and verification."""

    def __init__(self, global_config_gateway: GlobalConfigGateway) -> None:
        self._gateway = global_config_gateway

    def register_server(
        self,
        name: str,
        server_type_str: str,
        command: str | None,
        url: str | None,
        args: list[str],
    ) -> MCPServerConfig:
        """Validate inputs, create server config, and persist it.

        Raises
        ------
        MCPValidationError
            If the server type is invalid or required params are missing.
        """
        try:
            srv_type = MCPServerType(server_type_str.lower())
        except ValueError as e:
            raise MCPValidationError(
                f"Invalid server type '{server_type_str}'. Use 'stdio' or 'http'."
            ) from e

        if srv_type == MCPServerType.STDIO and not command:
            raise MCPValidationError("STDIO server requires --command parameter.")
        if srv_type == MCPServerType.HTTP and not url:
            raise MCPValidationError("HTTP server requires --url parameter.")

        try:
            config = MCPServerConfig(name=name, server_type=srv_type, command=command, url=url, args=args)
        except ValueError as e:
            raise MCPValidationError(str(e)) from e

        global_config = self._gateway.load()
        global_config.add_mcp_server(config)
        self._gateway.save(global_config)
        return config

    def remove_server(self, name: str) -> bool:
        """Remove a server from the global config.

        Returns
        -------
        bool
            True if the server was found and removed, False otherwise.
        """
        global_config = self._gateway.load()
        if global_config.remove_mcp_server(name):
            self._gateway.save(global_config)
            return True
        return False

    def list_servers(self) -> list[MCPServerConfig]:
        """Return all registered MCP servers."""
        return self._gateway.load().list_mcp_servers()

    def verify_server(self, server: MCPServerConfig) -> bool:
        """Check whether the given MCP server is reachable."""
        return verify_mcp_server(server)

    def get_server(self, name: str) -> MCPServerConfig | None:
        """Look up a server by name, returning None if not found."""
        return self._gateway.load().get_mcp_server(name)
