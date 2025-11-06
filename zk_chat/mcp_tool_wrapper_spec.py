"""
Tests for MCP tool wrapper functionality.
"""
from unittest.mock import Mock

from zk_chat.mcp_tool_wrapper import MCPToolWrapper


class DescribeMCPToolWrapper:
    """Tests for MCPToolWrapper class."""

    def should_create_wrapper_with_client(self):
        mock_client = Mock()
        mock_loop = Mock()
        tool_descriptor = {
            "name": "test_tool",
            "description": "A test tool",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"}
                }
            }
        }

        wrapper = MCPToolWrapper(mock_client, "test-server", "test_tool", tool_descriptor,
                                 mock_loop)

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
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "First parameter"
                    }
                },
                "required": ["param1"]
            }
        }

        wrapper = MCPToolWrapper(mock_client, "test-server", "test_tool", tool_descriptor,
                                 mock_loop)
        descriptor = wrapper.descriptor

        assert descriptor["type"] == "function"
        assert descriptor["function"]["name"] == "test_tool"
        assert descriptor["function"]["description"] == "A test tool that does something"
        assert "param1" in descriptor["function"]["parameters"]["properties"]

    def should_handle_missing_description(self):
        mock_client = Mock()
        mock_loop = Mock()
        tool_descriptor = {
            "name": "test_tool",
            "inputSchema": {}
        }

        wrapper = MCPToolWrapper(mock_client, "test-server", "test_tool", tool_descriptor,
                                 mock_loop)
        descriptor = wrapper.descriptor

        assert "Tool from test-server" in descriptor["function"]["description"]

    def should_coerce_string_to_number(self):
        mock_client = Mock()
        mock_loop = Mock()
        tool_descriptor = {
            "name": "test_tool",
            "description": "A test tool",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "timeout": {"type": "number"},
                    "count": {"type": "integer"}
                }
            }
        }

        wrapper = MCPToolWrapper(mock_client, "test-server", "test_tool", tool_descriptor,
                                 mock_loop)

        # Test coercion
        coerced = wrapper._coerce_types({"timeout": "30.5", "count": "42"})

        assert coerced["timeout"] == 30.5
        assert coerced["count"] == 42
        assert isinstance(coerced["timeout"], float)
        assert isinstance(coerced["count"], int)

    def should_coerce_string_to_boolean(self):
        mock_client = Mock()
        mock_loop = Mock()
        tool_descriptor = {
            "name": "test_tool",
            "description": "A test tool",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean"}
                }
            }
        }

        wrapper = MCPToolWrapper(mock_client, "test-server", "test_tool", tool_descriptor,
                                 mock_loop)

        # Test coercion
        assert wrapper._coerce_types({"enabled": "true"})["enabled"] is True
        assert wrapper._coerce_types({"enabled": "false"})["enabled"] is False
        assert wrapper._coerce_types({"enabled": "1"})["enabled"] is True
        assert wrapper._coerce_types({"enabled": "0"})["enabled"] is False
