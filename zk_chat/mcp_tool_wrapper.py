"""
MCP Tool Wrapper that adapts MCP server tools to mojentic LLMTool interface.

This module provides a wrapper that allows external MCP server tools to be used
as mojentic-compatible tools within zk-chat.
"""
import asyncio
from typing import Any

import structlog
from fastmcp import Client
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.global_config import GlobalConfig, MCPServerConfig, MCPServerType

logger = structlog.get_logger()


class MCPToolWrapper(LLMTool):
    """
    Wraps an MCP server tool to make it compatible with mojentic's LLMTool interface.

    This wrapper uses a shared Client connection managed by MCPClientManager.
    """

    def __init__(self, client: Client, server_name: str, tool_name: str,
                 tool_descriptor: dict[str, Any], loop: asyncio.AbstractEventLoop):
        """
        Initialize the MCP tool wrapper.

        Parameters
        ----------
        client : Client
            Shared MCP client connection (managed externally)
        server_name : str
            Name of the MCP server
        tool_name : str
            Name of the tool on the MCP server
        tool_descriptor : Dict[str, Any]
            Tool descriptor from the MCP server (mcp.types.Tool)
        loop : asyncio.AbstractEventLoop
            Event loop where the client is connected
        """
        self._client = client
        self.server_name = server_name
        self.tool_name = tool_name
        self.tool_descriptor = tool_descriptor
        self._loop = loop

    def _coerce_types(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Coerce argument types to match the input schema.

        LLMs sometimes return strings for numeric fields, so we need to convert them.

        Parameters
        ----------
        arguments : Dict[str, Any]
            Raw arguments from the LLM

        Returns
        -------
        Dict[str, Any]
            Arguments with types coerced to match schema
        """
        input_schema = self.tool_descriptor.get("inputSchema", {})
        properties = input_schema.get("properties", {})

        coerced = {}
        for key, value in arguments.items():
            if key in properties:
                prop_schema = properties[key]
                prop_type = prop_schema.get("type")

                # Coerce based on schema type
                if prop_type == "number" or prop_type == "integer":
                    if isinstance(value, str):
                        try:
                            coerced[key] = int(value) if prop_type == "integer" else float(value)
                        except (ValueError, TypeError):
                            coerced[key] = value
                    else:
                        coerced[key] = value
                elif prop_type == "boolean":
                    if isinstance(value, str):
                        coerced[key] = value.lower() in ("true", "1", "yes")
                    else:
                        coerced[key] = bool(value)
                else:
                    coerced[key] = value
            else:
                coerced[key] = value

        return coerced

    def run(self, **kwargs) -> str:
        """
        Execute the MCP tool with the given parameters.

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
                    server_name=self.server_name,
                    tool_name=self.tool_name,
                    parameters=kwargs)

        try:
            # Coerce types to match schema
            coerced_args = self._coerce_types(kwargs)

            # Schedule the async operation on the background loop
            future = asyncio.run_coroutine_threadsafe(self._async_run(coerced_args), self._loop)
            # Wait for the result
            result = future.result(timeout=60)  # 60 second timeout for tool execution
            result_str = str(result)
            logger.info("MCP tool execution completed",
                        server_name=self.server_name,
                        tool_name=self.tool_name,
                        result=result_str)
            return result_str
        except Exception as e:
            error_msg = f"Error executing MCP tool {self.tool_name}: {str(e)}"
            logger.error("MCP tool execution failed",
                         server_name=self.server_name,
                         tool_name=self.tool_name,
                         error=str(e))
            return error_msg

    async def _async_run(self, arguments: dict[str, Any]) -> Any:
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
        result = await self._client.call_tool(self.tool_name, arguments)
        return result

    @property
    def descriptor(self) -> dict[str, Any]:
        """
        Get the tool descriptor in mojentic format.

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
                "description": self.tool_descriptor.get("description",
                                                        f"Tool from {self.server_name}"),
                "parameters": input_schema
            }
        }

        return descriptor


class MCPClientManager:
    """
    Manages MCP client connections for all registered servers.

    This manager:
    - Creates one Client per MCP server
    - Maintains connections for the session lifetime
    - Discovers and provides tools from all servers
    - Handles proper connection lifecycle
    - Runs a persistent event loop in a background thread
    """

    def __init__(self):
        """Initialize the MCP client manager."""
        self._clients: dict[str, Client] = {}
        self._tools: list[MCPToolWrapper] = []
        self._initialized = False
        self._loop: asyncio.AbstractEventLoop | None = None
        self._loop_thread = None

    def __enter__(self):
        """Context manager entry - initialize all clients synchronously."""
        self.initialize_sync()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup all clients synchronously."""
        self.cleanup_sync()

    async def __aenter__(self):
        """Async context manager entry - initialize all clients."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup all clients."""
        await self.cleanup()

    def _start_event_loop(self):
        """Start a background event loop in a separate thread."""
        import threading

        def run_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=run_loop, args=(self._loop,), daemon=True)
        self._loop_thread.start()

        logger.info("Started background event loop for MCP clients")

    def _stop_event_loop(self):
        """Stop the background event loop."""
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
            if self._loop_thread:
                self._loop_thread.join(timeout=5)
            self._loop.close()
            logger.info("Stopped background event loop")

    def initialize_sync(self):
        """Initialize connections synchronously by running async code in background loop."""

        # Start the background event loop
        self._start_event_loop()

        # Schedule initialization on the background loop
        future = asyncio.run_coroutine_threadsafe(self.initialize(), self._loop)

        # Wait for initialization to complete
        future.result()

    def cleanup_sync(self):
        """Cleanup connections synchronously by running async code in background loop."""
        import concurrent.futures

        if self._loop and self._loop.is_running():
            # Schedule cleanup on the background loop
            future = asyncio.run_coroutine_threadsafe(self.cleanup(), self._loop)

            # Wait for cleanup to complete
            try:
                future.result(timeout=10)
            except concurrent.futures.TimeoutError:
                logger.error("Timeout waiting for MCP client cleanup")

        # Stop the event loop
        self._stop_event_loop()

    async def initialize(self):
        """
        Initialize connections to all registered MCP servers.

        This method:
        1. Loads server configurations
        2. Creates Client instances
        3. Connects to servers
        4. Discovers available tools
        """
        if self._initialized:
            logger.warning("MCPClientManager already initialized")
            return

        global_config = GlobalConfig.load()
        servers = global_config.list_mcp_servers()

        if not servers:
            logger.info("No MCP servers registered")
            self._initialized = True
            return

        logger.info("Initializing MCP client connections", server_count=len(servers))

        for server_config in servers:
            try:
                await self._connect_server(server_config)
            except Exception as e:
                logger.error("Failed to connect to MCP server",
                             server_name=server_config.name,
                             error=str(e))

        logger.info("MCP client initialization complete",
                    connected_servers=len(self._clients),
                    total_tools=len(self._tools))

        self._initialized = True

    async def _connect_server(self, server_config: MCPServerConfig):
        """
        Connect to a single MCP server and discover its tools.

        Parameters
        ----------
        server_config : MCPServerConfig
            Configuration for the MCP server
        """
        logger.info("Connecting to MCP server", server_name=server_config.name)

        # Create client based on server type
        if server_config.server_type == MCPServerType.STDIO:
            # FastMCP Client expects config in mcpServers format for STDIO
            client_config = {
                "mcpServers": {
                    server_config.name: {
                        "command": server_config.command,
                        "args": server_config.args or []
                    }
                }
            }
            client = Client(client_config)
        elif server_config.server_type == MCPServerType.HTTP:
            # For HTTP, can pass URL directly
            client = Client(server_config.url)
        else:
            raise ValueError(f"Unsupported server type: {server_config.server_type}")

        # Connect and initialize
        await client.__aenter__()
        self._clients[server_config.name] = client

        logger.info("Connected to MCP server", server_name=server_config.name)

        # Discover tools
        await self._discover_tools(server_config, client)

    async def _discover_tools(self, server_config: MCPServerConfig, client: Client):
        """
        Discover tools from a connected MCP server.

        Parameters
        ----------
        server_config : MCPServerConfig
            Configuration for the MCP server
        client : Client
            Connected MCP client
        """
        logger.info("Discovering tools from MCP server", server_name=server_config.name)

        try:
            tools = await client.list_tools()

            for tool in tools:
                tool_dict = {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }

                wrapper = MCPToolWrapper(
                    client=client,
                    server_name=server_config.name,
                    tool_name=tool.name,
                    tool_descriptor=tool_dict,
                    loop=self._loop
                )
                self._tools.append(wrapper)

                logger.info("Discovered MCP tool",
                            server_name=server_config.name,
                            tool_name=tool.name)

            logger.info("Tool discovery complete",
                        server_name=server_config.name,
                        tool_count=len(
                            [t for t in self._tools if t.server_name == server_config.name]))

        except Exception as e:
            logger.error("Failed to discover tools from MCP server",
                         server_name=server_config.name,
                         error=str(e))

    async def cleanup(self):
        """Cleanup all client connections."""
        if not self._initialized:
            return

        logger.info("Cleaning up MCP client connections", client_count=len(self._clients))

        for server_name, client in self._clients.items():
            try:
                await client.__aexit__(None, None, None)
                logger.info("Disconnected from MCP server", server_name=server_name)
            except Exception as e:
                logger.error("Error disconnecting from MCP server",
                             server_name=server_name,
                             error=str(e))

        self._clients.clear()
        self._tools.clear()
        self._initialized = False

    def get_tools(self) -> list[LLMTool]:
        """
        Get all discovered tools from connected MCP servers.

        Returns
        -------
        List[LLMTool]
            List of all wrapped MCP tools
        """
        return self._tools.copy()


def load_mcp_tools_from_registered_servers() -> list[LLMTool]:
    """
    DEPRECATED: Use MCPClientManager instead.

    This function is kept for backwards compatibility but will create
    and immediately destroy connections (inefficient).

    Returns
    -------
    List[LLMTool]
        Empty list - this function is deprecated
    """
    logger.warning(
        "load_mcp_tools_from_registered_servers is deprecated. Use MCPClientManager instead.")
    return []
