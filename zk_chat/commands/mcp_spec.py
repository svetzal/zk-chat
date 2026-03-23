"""
Tests for MCP command helper functions.
"""

from unittest.mock import Mock

import pytest

from zk_chat.commands.mcp import _register_server, _remove_server
from zk_chat.global_config import GlobalConfig, MCPServerConfig, MCPServerType
from zk_chat.global_config_gateway import GlobalConfigGateway


@pytest.fixture
def mock_gateway():
    return Mock(spec=GlobalConfigGateway)


class DescribeRegisterServer:
    """Tests for the _register_server helper function."""

    def should_load_config_add_server_and_save(self, mock_gateway):
        config = GlobalConfig()
        mock_gateway.load.return_value = config
        server_config = MCPServerConfig(name="test-server", server_type=MCPServerType.STDIO, command="test-cmd")

        _register_server(server_config, mock_gateway)

        mock_gateway.load.assert_called_once()
        mock_gateway.save.assert_called_once_with(config)
        assert config.get_mcp_server("test-server") is not None

    def should_add_server_to_existing_config(self, mock_gateway):
        config = GlobalConfig()
        existing = MCPServerConfig(name="existing", server_type=MCPServerType.STDIO, command="cmd")
        config.add_mcp_server(existing)
        mock_gateway.load.return_value = config
        new_server = MCPServerConfig(name="new-server", server_type=MCPServerType.HTTP, url="http://localhost")

        _register_server(new_server, mock_gateway)

        assert config.get_mcp_server("new-server") is not None
        assert config.get_mcp_server("existing") is not None


class DescribeRemoveServer:
    """Tests for the _remove_server helper function."""

    def should_return_true_when_server_exists(self, mock_gateway):
        config = GlobalConfig()
        server = MCPServerConfig(name="my-server", server_type=MCPServerType.STDIO, command="cmd")
        config.add_mcp_server(server)
        mock_gateway.load.return_value = config

        result = _remove_server("my-server", mock_gateway)

        assert result is True
        mock_gateway.save.assert_called_once()

    def should_return_false_when_server_not_found(self, mock_gateway):
        mock_gateway.load.return_value = GlobalConfig()

        result = _remove_server("nonexistent", mock_gateway)

        assert result is False
        mock_gateway.save.assert_not_called()

    def should_use_gateway_to_save_after_removal(self, mock_gateway):
        config = GlobalConfig()
        server = MCPServerConfig(name="my-server", server_type=MCPServerType.STDIO, command="cmd")
        config.add_mcp_server(server)
        mock_gateway.load.return_value = config

        _remove_server("my-server", mock_gateway)

        mock_gateway.save.assert_called_once_with(config)
