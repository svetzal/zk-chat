"""
MCP Tool Wrapper that adapts MCP server tools to mojentic LLMTool interface.

This module provides a wrapper that allows external MCP server tools to be used
as mojentic-compatible tools within zk-chat.
"""
import asyncio
from typing import Any, Dict, List, Optional

import structlog
from fastmcp import Client
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.global_config import GlobalConfig, MCPServerConfig, MCPServerType

logger = structlog.get_logger()


class MCPToolWrapper(LLMTool):
    """
    Wraps an MCP server tool to make it compatible with mojentic's LLMTool interface.

    This wrapper:
    - Connects to an external MCP server (STDIO or HTTP)
    - Exposes the MCP tool as a mojentic-compatible tool
    - Handles async/sync conversion for tool calls
    - Manages the client connection lifecycle
    """

    def __init__(self, server_config: MCPServerConfig, tool_name: str, tool_descriptor: Dict[str, Any]):
        """
        Initialize the MCP tool wrapper.

        Parameters
        ----------
        server_config : MCPServerConfig
            Configuration for the MCP server
        tool_name : str
            Name of the tool on the MCP server
        tool_descriptor : Dict[str, Any]
            Tool descriptor from the MCP server (mcp.types.Tool)
        """
        self.server_config = server_config
        self.tool_name = tool_name
        self.tool_descriptor = tool_descriptor
        self._client: Optional[Client] = None

    def _get_client(self) -> Client:
        """Get or create the MCP client."""
        if self._client is None:
            if self.server_config.server_type == MCPServerType.STDIO:
                command_args = [self.server_config.command] + (self.server_config.args or [])
                transport_config = {
                    "command": command_args[0],
                    "args": command_args[1:] if len(command_args) > 1 else [],
                    "env": None
                }
                self._client = Client(transport_config)
            elif self.server_config.server_type == MCPServerType.HTTP:
                self._client = Client(self.server_config.url)
            else:
                raise ValueError(f"Unsupported server type: {self.server_config.server_type}")

            logger.info("Created MCP client",
                        server_name=self.server_config.name,
                        tool_name=self.tool_name)

        return self._client

    def run(self, **kwargs) -> str:
        """
        Execute the MCP tool with the given parameters.

        This method converts the synchronous call to async and back,
        managing the client connection lifecycle.

        Parameters
        ----------
        **kwargs
            Tool parameters as keyword arguments

        Returns
        -------
        str
            Tool execution result as a string
        """
        logger.info("Executing MCP tool",
                    server_name=self.server_config.name,
                    tool_name=self.tool_name,
                    parameters=kwargs)

        try:
            result = asyncio.run(self._async_run(kwargs))
            result_str = str(result)
            logger.info("MCP tool execution completed",
                        server_name=self.server_config.name,
                        tool_name=self.tool_name,
                        result=result_str)
            return result_str
        except Exception as e:
            error_msg = f"Error executing MCP tool {self.tool_name}: {str(e)}"
            logger.error("MCP tool execution failed",
                         server_name=self.server_config.name,
                         tool_name=self.tool_name,
                         error=str(e))
            return error_msg

    async def _async_run(self, arguments: Dict[str, Any]) -> Any:
        """
        Async implementation of tool execution.

        Parameters
        ----------
        arguments : Dict[str, Any]
            Tool parameters

        Returns
        -------
        Any
            Tool execution result
        """
        client = self._get_client()

        async with client:
            result = await client.call_tool(self.tool_name, arguments)
            return result

    @property
    def descriptor(self) -> Dict[str, Any]:
        """
        Get the tool descriptor in mojentic format.

        This converts the MCP tool descriptor to the format expected by mojentic.

        Returns
        -------
        Dict[str, Any]
            Tool descriptor in mojentic format
        """
        input_schema = self.tool_descriptor.get("inputSchema", {})

        descriptor = {
            "type": "function",
            "function": {
                "name": self.tool_name,
                "description": self.tool_descriptor.get("description", f"Tool from {self.server_config.name}"),
                "parameters": input_schema
            }
        }

        return descriptor

    def close(self):
        """Close the MCP client connection."""
        if self._client is not None:
            asyncio.run(self._client.close())
            self._client = None
            logger.info("Closed MCP client",
                        server_name=self.server_config.name,
                        tool_name=self.tool_name)


async def discover_mcp_tools(server_config: MCPServerConfig) -> List[MCPToolWrapper]:
    """
    Discover all tools available on an MCP server and wrap them.

    Parameters
    ----------
    server_config : MCPServerConfig
        Configuration for the MCP server

    Returns
    -------
    List[MCPToolWrapper]
        List of wrapped MCP tools
    """
    logger.info("Discovering tools from MCP server", server_name=server_config.name)

    try:
        if server_config.server_type == MCPServerType.STDIO:
            command_args = [server_config.command] + (server_config.args or [])
            transport_config = {
                "command": command_args[0],
                "args": command_args[1:] if len(command_args) > 1 else [],
                "env": None
            }
            client = Client(transport_config)
        elif server_config.server_type == MCPServerType.HTTP:
            client = Client(server_config.url)
        else:
            logger.error("Unsupported server type", server_name=server_config.name)
            return []

        async with client:
            tools = await client.list_tools()

            wrapped_tools = []
            for tool in tools:
                tool_dict = {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }

                wrapper = MCPToolWrapper(
                    server_config=server_config,
                    tool_name=tool.name,
                    tool_descriptor=tool_dict
                )
                wrapped_tools.append(wrapper)

                logger.info("Discovered MCP tool",
                            server_name=server_config.name,
                            tool_name=tool.name)

            logger.info("Tool discovery complete",
                        server_name=server_config.name,
                        tool_count=len(wrapped_tools))

            return wrapped_tools

    except Exception as e:
        logger.error("Failed to discover tools from MCP server",
                     server_name=server_config.name,
                     error=str(e))
        return []


def load_mcp_tools_from_registered_servers() -> List[MCPToolWrapper]:
    """
    Load all tools from registered MCP servers.

    This function discovers tools from all registered MCP servers
    that are currently available.

    Returns
    -------
    List[MCPToolWrapper]
        List of all wrapped MCP tools from available servers
    """
    global_config = GlobalConfig.load()
    servers = global_config.list_mcp_servers()

    if not servers:
        logger.info("No MCP servers registered")
        return []

    all_tools = []

    for server_config in servers:
        try:
            tools = asyncio.run(discover_mcp_tools(server_config))
            all_tools.extend(tools)
        except Exception as e:
            logger.warning("Failed to load tools from MCP server",
                           server_name=server_config.name,
                           error=str(e))

    logger.info("Loaded MCP tools from registered servers", total_tools=len(all_tools))

    return all_tools
