"""
Tests for MCP server management in GlobalConfig.
"""
from unittest.mock import patch

from zk_chat.global_config import GlobalConfig, MCPServerConfig, MCPServerType


class DescribeGlobalConfigMCPServers:
    """Tests for MCP server management in GlobalConfig."""

    def should_add_stdio_mcp_server(self):
        config = GlobalConfig()
        server = MCPServerConfig(
            name="test-server",
            server_type=MCPServerType.STDIO,
            command="test-command",
            args=["--arg1", "value1"]
        )

        with patch('zk_chat.global_config.GlobalConfig.save'):
            config.add_mcp_server(server)

        assert "test-server" in config.mcp_servers
        assert config.mcp_servers["test-server"].command == "test-command"

    def should_add_http_mcp_server(self):
        config = GlobalConfig()
        server = MCPServerConfig(
            name="http-server",
            server_type=MCPServerType.HTTP,
            url="http://localhost:8080"
        )

        with patch('zk_chat.global_config.GlobalConfig.save'):
            config.add_mcp_server(server)

        assert "http-server" in config.mcp_servers
        assert config.mcp_servers["http-server"].url == "http://localhost:8080"

    def should_remove_mcp_server(self):
        config = GlobalConfig()
        server = MCPServerConfig(
            name="test-server",
            server_type=MCPServerType.STDIO,
            command="test-command"
        )

        with patch('zk_chat.global_config.GlobalConfig.save'):
            config.add_mcp_server(server)
            result = config.remove_mcp_server("test-server")

        assert result is True
        assert "test-server" not in config.mcp_servers

    def should_return_false_when_removing_nonexistent_server(self):
        config = GlobalConfig()

        with patch('zk_chat.global_config.GlobalConfig.save'):
            result = config.remove_mcp_server("nonexistent")

        assert result is False

    def should_get_mcp_server_by_name(self):
        config = GlobalConfig()
        server = MCPServerConfig(
            name="test-server",
            server_type=MCPServerType.STDIO,
            command="test-command"
        )

        with patch('zk_chat.global_config.GlobalConfig.save'):
            config.add_mcp_server(server)

        retrieved = config.get_mcp_server("test-server")

        assert retrieved is not None
        assert retrieved.name == "test-server"
        assert retrieved.command == "test-command"

    def should_return_none_for_nonexistent_server(self):
        config = GlobalConfig()

        retrieved = config.get_mcp_server("nonexistent")

        assert retrieved is None

    def should_list_all_mcp_servers(self):
        config = GlobalConfig()
        server1 = MCPServerConfig(
            name="server1",
            server_type=MCPServerType.STDIO,
            command="command1"
        )
        server2 = MCPServerConfig(
            name="server2",
            server_type=MCPServerType.HTTP,
            url="http://localhost:8080"
        )

        with patch('zk_chat.global_config.GlobalConfig.save'):
            config.add_mcp_server(server1)
            config.add_mcp_server(server2)

        servers = config.list_mcp_servers()

        assert len(servers) == 2
        assert any(s.name == "server1" for s in servers)
        assert any(s.name == "server2" for s in servers)

    def should_update_existing_server(self):
        config = GlobalConfig()
        server1 = MCPServerConfig(
            name="test-server",
            server_type=MCPServerType.STDIO,
            command="old-command"
        )
        server2 = MCPServerConfig(
            name="test-server",
            server_type=MCPServerType.STDIO,
            command="new-command"
        )

        with patch('zk_chat.global_config.GlobalConfig.save'):
            config.add_mcp_server(server1)
            config.add_mcp_server(server2)

        assert len(config.mcp_servers) == 1
        assert config.mcp_servers["test-server"].command == "new-command"


class DescribeMCPServerConfig:
    """Tests for MCPServerConfig validation."""

    def should_validate_stdio_server_requires_command(self):
        try:
            MCPServerConfig(
                name="test",
                server_type=MCPServerType.STDIO
            )
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "command" in str(e)

    def should_validate_http_server_requires_url(self):
        try:
            MCPServerConfig(
                name="test",
                server_type=MCPServerType.HTTP
            )
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "URL" in str(e)

    def should_create_stdio_server_with_command(self):
        server = MCPServerConfig(
            name="test",
            server_type=MCPServerType.STDIO,
            command="test-command"
        )

        assert server.name == "test"
        assert server.server_type == MCPServerType.STDIO
        assert server.command == "test-command"

    def should_create_http_server_with_url(self):
        server = MCPServerConfig(
            name="test",
            server_type=MCPServerType.HTTP,
            url="http://localhost:8080"
        )

        assert server.name == "test"
        assert server.server_type == MCPServerType.HTTP
        assert server.url == "http://localhost:8080"

    def should_create_stdio_server_with_args(self):
        server = MCPServerConfig(
            name="test",
            server_type=MCPServerType.STDIO,
            command="test-command",
            args=["--flag", "value"]
        )

        assert server.args == ["--flag", "value"]
