"""
Tests for MCP tool wrapper functionality.
"""
from zk_chat.global_config import MCPServerConfig, MCPServerType
from zk_chat.mcp_tool_wrapper import MCPToolWrapper


class DescribeMCPToolWrapper:
    """Tests for MCPToolWrapper class."""

    def should_create_wrapper_for_stdio_server(self):
        server_config = MCPServerConfig(
            name="test-server",
            server_type=MCPServerType.STDIO,
            command="test-command"
        )
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

        wrapper = MCPToolWrapper(server_config, "test_tool", tool_descriptor)

        assert wrapper.tool_name == "test_tool"
        assert wrapper.server_config.name == "test-server"

    def should_create_wrapper_for_http_server(self):
        server_config = MCPServerConfig(
            name="test-server",
            server_type=MCPServerType.HTTP,
            url="http://localhost:8080"
        )
        tool_descriptor = {
            "name": "test_tool",
            "description": "A test tool",
            "inputSchema": {}
        }

        wrapper = MCPToolWrapper(server_config, "test_tool", tool_descriptor)

        assert wrapper.tool_name == "test_tool"
        assert wrapper.server_config.url == "http://localhost:8080"

    def should_generate_mojentic_compatible_descriptor(self):
        server_config = MCPServerConfig(
            name="test-server",
            server_type=MCPServerType.STDIO,
            command="test-command"
        )
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

        wrapper = MCPToolWrapper(server_config, "test_tool", tool_descriptor)
        descriptor = wrapper.descriptor

        assert descriptor["type"] == "function"
        assert descriptor["function"]["name"] == "test_tool"
        assert descriptor["function"]["description"] == "A test tool that does something"
        assert "param1" in descriptor["function"]["parameters"]["properties"]

    def should_handle_missing_description(self):
        server_config = MCPServerConfig(
            name="test-server",
            server_type=MCPServerType.STDIO,
            command="test-command"
        )
        tool_descriptor = {
            "name": "test_tool",
            "inputSchema": {}
        }

        wrapper = MCPToolWrapper(server_config, "test_tool", tool_descriptor)
        descriptor = wrapper.descriptor

        assert "Tool from test-server" in descriptor["function"]["description"]
