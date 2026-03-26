"""
Tests for MCP client server verification functionality.
"""

from unittest.mock import Mock, patch

import requests

from zk_chat.global_config import GlobalConfig, MCPServerConfig, MCPServerType
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.mcp_client import verify_all_mcp_servers, verify_http_server, verify_mcp_server, verify_stdio_server


class DescribeVerifyStdioServer:
    """Tests for STDIO server verification."""

    def should_return_true_when_command_exists(self):
        server_config = MCPServerConfig(name="test-server", server_type=MCPServerType.STDIO, command="python")

        with patch("shutil.which", return_value="/usr/bin/python"):
            result = verify_stdio_server(server_config)

        assert result is True

    def should_return_false_when_command_not_found(self):
        server_config = MCPServerConfig(
            name="test-server", server_type=MCPServerType.STDIO, command="nonexistent-command"
        )

        with patch("shutil.which", return_value=None):
            result = verify_stdio_server(server_config)

        assert result is False

    def should_return_false_for_non_stdio_server(self):
        server_config = MCPServerConfig(name="test-server", server_type=MCPServerType.HTTP, url="http://localhost:8080")

        result = verify_stdio_server(server_config)

        assert result is False

    def should_handle_exceptions_gracefully(self):
        server_config = MCPServerConfig(name="test-server", server_type=MCPServerType.STDIO, command="test-command")

        with patch("shutil.which", side_effect=Exception("Test error")):
            result = verify_stdio_server(server_config)

        assert result is False


class DescribeVerifyHttpServer:
    """Tests for HTTP server verification."""

    def should_return_true_when_server_reachable(self):
        server_config = MCPServerConfig(name="test-server", server_type=MCPServerType.HTTP, url="http://localhost:8080")
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200

        with patch("requests.get", return_value=mock_response):
            result = verify_http_server(server_config)

        assert result is True

    def should_return_false_when_non_200_status(self):
        server_config = MCPServerConfig(name="test-server", server_type=MCPServerType.HTTP, url="http://localhost:8080")
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 404

        with patch("requests.get", return_value=mock_response):
            result = verify_http_server(server_config)

        assert result is False

    def should_return_false_when_request_fails(self):
        server_config = MCPServerConfig(name="test-server", server_type=MCPServerType.HTTP, url="http://localhost:8080")

        with patch("requests.get", side_effect=Exception("Connection error")):
            result = verify_http_server(server_config)

        assert result is False

    def should_return_false_for_non_http_server(self):
        server_config = MCPServerConfig(name="test-server", server_type=MCPServerType.STDIO, command="test-command")

        result = verify_http_server(server_config)

        assert result is False


class DescribeVerifyMcpServer:
    """Tests for generic MCP server verification."""

    def should_verify_stdio_server(self):
        server_config = MCPServerConfig(name="test-server", server_type=MCPServerType.STDIO, command="python")

        with patch("shutil.which", return_value="/usr/bin/python"):
            result = verify_mcp_server(server_config)

        assert result is True

    def should_verify_http_server(self):
        server_config = MCPServerConfig(name="test-server", server_type=MCPServerType.HTTP, url="http://localhost:8080")
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200

        with patch("requests.get", return_value=mock_response):
            result = verify_mcp_server(server_config)

        assert result is True


class DescribeVerifyAllMcpServers:
    """Tests for verify_all_mcp_servers with injected gateway."""

    def should_use_injected_gateway_to_load_config(self):
        mock_gateway = Mock(spec=GlobalConfigGateway)
        mock_gateway.load.return_value = GlobalConfig()

        result = verify_all_mcp_servers(mock_gateway)

        mock_gateway.load.assert_called_once()
        assert result == []

    def should_return_empty_list_when_no_servers_registered(self):
        mock_gateway = Mock(spec=GlobalConfigGateway)
        mock_gateway.load.return_value = GlobalConfig()

        result = verify_all_mcp_servers(mock_gateway)

        assert result == []

    def should_return_unavailable_server_names(self):
        server = MCPServerConfig(name="missing-cmd", server_type=MCPServerType.STDIO, command="nonexistent-cmd")
        global_config = GlobalConfig()
        global_config.add_mcp_server(server)
        mock_gateway = Mock(spec=GlobalConfigGateway)
        mock_gateway.load.return_value = global_config

        with patch("shutil.which", return_value=None):
            result = verify_all_mcp_servers(mock_gateway)

        assert result == ["missing-cmd"]
