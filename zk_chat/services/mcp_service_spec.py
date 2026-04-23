"""Tests for MCPService."""

from unittest.mock import Mock

import pytest

from zk_chat.global_config import GlobalConfig, MCPServerConfig, MCPServerType
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.services.mcp_service import MCPService, MCPValidationError


@pytest.fixture
def mock_gateway():
    return Mock(spec=GlobalConfigGateway)


@pytest.fixture
def mock_global_config():
    return Mock(spec=GlobalConfig)


@pytest.fixture
def service(mock_gateway):
    return MCPService(mock_gateway)


class DescribeMCPService:
    """Tests for the MCPService component."""

    def should_be_instantiated_with_global_config_gateway(self, mock_gateway):
        svc = MCPService(mock_gateway)

        assert isinstance(svc, MCPService)

    class DescribeRegisterServer:
        def should_register_valid_stdio_server(self, service, mock_gateway, mock_global_config):
            mock_gateway.load.return_value = mock_global_config

            result = service.register_server("figma", "stdio", "figma-mcp", None, [])

            assert result.name == "figma"
            assert result.server_type == MCPServerType.STDIO
            assert result.command == "figma-mcp"
            mock_global_config.add_mcp_server.assert_called_once_with(result)
            mock_gateway.save.assert_called_once_with(mock_global_config)

        def should_register_valid_http_server(self, service, mock_gateway, mock_global_config):
            mock_gateway.load.return_value = mock_global_config

            result = service.register_server("chrome", "http", None, "http://localhost:8080", [])

            assert result.name == "chrome"
            assert result.server_type == MCPServerType.HTTP
            assert result.url == "http://localhost:8080"

        def should_register_server_with_args(self, service, mock_gateway, mock_global_config):
            mock_gateway.load.return_value = mock_global_config

            result = service.register_server("custom", "stdio", "my-mcp", None, ["--flag1", "--flag2"])

            assert result.args == ["--flag1", "--flag2"]

        def should_raise_on_invalid_server_type(self, service):
            with pytest.raises(MCPValidationError) as exc_info:
                service.register_server("bad", "grpc", None, None, [])

            assert "Invalid server type" in str(exc_info.value)
            assert "grpc" in str(exc_info.value)

        def should_raise_when_stdio_missing_command(self, service):
            with pytest.raises(MCPValidationError) as exc_info:
                service.register_server("bad", "stdio", None, None, [])

            assert "STDIO server requires --command" in str(exc_info.value)

        def should_raise_when_http_missing_url(self, service):
            with pytest.raises(MCPValidationError) as exc_info:
                service.register_server("bad", "http", None, None, [])

            assert "HTTP server requires --url" in str(exc_info.value)

    class DescribeRemoveServer:
        def should_remove_existing_server_and_return_true(self, service, mock_gateway, mock_global_config):
            mock_gateway.load.return_value = mock_global_config
            mock_global_config.remove_mcp_server.return_value = True

            result = service.remove_server("figma")

            assert result is True
            mock_global_config.remove_mcp_server.assert_called_once_with("figma")
            mock_gateway.save.assert_called_once_with(mock_global_config)

        def should_return_false_when_server_not_found(self, service, mock_gateway, mock_global_config):
            mock_gateway.load.return_value = mock_global_config
            mock_global_config.remove_mcp_server.return_value = False

            result = service.remove_server("nonexistent")

            assert result is False
            mock_gateway.save.assert_not_called()

    class DescribeListServers:
        def should_return_all_registered_servers(self, service, mock_gateway, mock_global_config):
            test_server = MCPServerConfig(name="figma", server_type=MCPServerType.STDIO, command="figma-mcp")
            mock_global_config.list_mcp_servers.return_value = [test_server]
            mock_gateway.load.return_value = mock_global_config

            result = service.list_servers()

            assert result == [test_server]

        def should_return_empty_list_when_no_servers(self, service, mock_gateway, mock_global_config):
            mock_global_config.list_mcp_servers.return_value = []
            mock_gateway.load.return_value = mock_global_config

            result = service.list_servers()

            assert result == []

    class DescribeGetServer:
        def should_return_server_config_by_name(self, service, mock_gateway, mock_global_config):
            test_server = MCPServerConfig(name="figma", server_type=MCPServerType.STDIO, command="figma-mcp")
            mock_global_config.get_mcp_server.return_value = test_server
            mock_gateway.load.return_value = mock_global_config

            result = service.get_server("figma")

            assert result is test_server
            mock_global_config.get_mcp_server.assert_called_once_with("figma")

        def should_return_none_when_server_not_found(self, service, mock_gateway, mock_global_config):
            mock_global_config.get_mcp_server.return_value = None
            mock_gateway.load.return_value = mock_global_config

            result = service.get_server("nonexistent")

            assert result is None
