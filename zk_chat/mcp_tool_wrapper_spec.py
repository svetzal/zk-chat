"""
Tests for MCP tool wrapper functionality.
"""

from unittest.mock import Mock

from zk_chat.global_config import GlobalConfig
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.mcp_tool_wrapper import MCPClientManager, MCPToolWrapper, coerce_types


class DescribeCoerceTypes:
    """Tests for the coerce_types module-level pure function."""

    def should_coerce_string_to_float_for_number_type(self):
        input_schema = {"properties": {"timeout": {"type": "number"}}}

        result = coerce_types({"timeout": "30.5"}, input_schema)

        assert result["timeout"] == 30.5
        assert isinstance(result["timeout"], float)

    def should_coerce_string_to_int_for_integer_type(self):
        input_schema = {"properties": {"count": {"type": "integer"}}}

        result = coerce_types({"count": "42"}, input_schema)

        assert result["count"] == 42
        assert isinstance(result["count"], int)

    def should_coerce_string_to_boolean_true(self):
        input_schema = {"properties": {"enabled": {"type": "boolean"}}}

        assert coerce_types({"enabled": "true"}, input_schema)["enabled"] is True
        assert coerce_types({"enabled": "1"}, input_schema)["enabled"] is True
        assert coerce_types({"enabled": "yes"}, input_schema)["enabled"] is True

    def should_coerce_string_to_boolean_false(self):
        input_schema = {"properties": {"enabled": {"type": "boolean"}}}

        assert coerce_types({"enabled": "false"}, input_schema)["enabled"] is False
        assert coerce_types({"enabled": "0"}, input_schema)["enabled"] is False
        assert coerce_types({"enabled": "no"}, input_schema)["enabled"] is False

    def should_pass_through_unknown_properties(self):
        input_schema = {"properties": {"known": {"type": "string"}}}

        result = coerce_types({"unknown": "value", "known": "text"}, input_schema)

        assert result["unknown"] == "value"
        assert result["known"] == "text"

    def should_handle_empty_schema(self):
        result = coerce_types({"key": "value"}, {})

        assert result["key"] == "value"

    def should_pass_through_invalid_number_string_unchanged(self):
        input_schema = {"properties": {"count": {"type": "integer"}}}

        result = coerce_types({"count": "not_a_number"}, input_schema)

        assert result["count"] == "not_a_number"

    def should_coerce_non_string_value_to_boolean(self):
        input_schema = {"properties": {"flag": {"type": "boolean"}}}

        assert coerce_types({"flag": 1}, input_schema)["flag"] is True
        assert coerce_types({"flag": 0}, input_schema)["flag"] is False


class DescribeMCPToolWrapper:
    """Tests for MCPToolWrapper class."""

    def should_create_wrapper_with_client(self):
        mock_client = Mock()
        mock_loop = Mock()
        tool_descriptor = {
            "name": "test_tool",
            "description": "A test tool",
            "inputSchema": {"type": "object", "properties": {"param1": {"type": "string"}}},
        }

        wrapper = MCPToolWrapper(mock_client, "test-server", "test_tool", tool_descriptor, mock_loop)

        assert wrapper.tool_name == "test_tool"
        assert wrapper.server_name == "test-server"
        assert wrapper._client == mock_client
        assert wrapper._loop == mock_loop

    def should_generate_mojentic_compatible_descriptor(self):
        mock_client = Mock()
        mock_loop = Mock()
        tool_descriptor = {
            "name": "test_tool",
            "description": "A test tool that does something",
            "inputSchema": {
                "type": "object",
                "properties": {"param1": {"type": "string", "description": "First parameter"}},
                "required": ["param1"],
            },
        }

        wrapper = MCPToolWrapper(mock_client, "test-server", "test_tool", tool_descriptor, mock_loop)
        descriptor = wrapper.descriptor

        assert descriptor["type"] == "function"
        assert descriptor["function"]["name"] == "test_tool"
        assert descriptor["function"]["description"] == "A test tool that does something"
        assert "param1" in descriptor["function"]["parameters"]["properties"]

    def should_handle_missing_description(self):
        mock_client = Mock()
        mock_loop = Mock()
        tool_descriptor = {"name": "test_tool", "inputSchema": {}}

        wrapper = MCPToolWrapper(mock_client, "test-server", "test_tool", tool_descriptor, mock_loop)
        descriptor = wrapper.descriptor

        assert "Tool from test-server" in descriptor["function"]["description"]


class DescribeMCPClientManager:
    """Tests for MCPClientManager initialization and dependency injection."""

    def should_accept_injected_global_config_gateway(self):
        mock_gateway = Mock(spec=GlobalConfigGateway)
        mock_gateway.load.return_value = GlobalConfig()

        manager = MCPClientManager(mock_gateway)

        assert manager._global_config_gateway is mock_gateway

    def should_use_default_global_config_gateway_when_none_provided(self):
        manager = MCPClientManager()

        assert isinstance(manager._global_config_gateway, GlobalConfigGateway)

    def should_use_injected_gateway_when_loading_servers(self):
        mock_gateway = Mock(spec=GlobalConfigGateway)
        mock_config = GlobalConfig()
        mock_gateway.load.return_value = mock_config

        manager = MCPClientManager(mock_gateway)
        manager._initialized = False

        import asyncio

        asyncio.run(manager.initialize())

        mock_gateway.load.assert_called_once()
