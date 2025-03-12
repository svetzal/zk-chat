"""
Model Context Protocol (MCP) server for ZK Chat tools.

This module provides an MCP implementation that directly bridges to the specific
tools used in the ZK Chat application.
"""
import json
from typing import Any, Dict, List, Optional

import structlog

from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.tools.create_or_overwrite_zk_document import CreateOrOverwriteZkDocument
from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo
from zk_chat.tools.read_zk_document import ReadZkDocument
from zk_chat.tools.retrieve_from_smart_memory import RetrieveFromSmartMemory
from zk_chat.tools.store_in_smart_memory import StoreInSmartMemory
from zk_chat.zettelkasten import Zettelkasten

# Initialize logger
logger = structlog.get_logger()

class MCPServer:
    """
    Model Context Protocol server that wraps specific ZK Chat tools.
    
    This server provides an MCP-compatible interface to the predefined tools
    used in the ZK Chat application.
    """
    
    def __init__(
        self, 
        zk: Zettelkasten,
        smart_memory: SmartMemory,
        enable_unsafe_operations: bool = False
    ):
        """
        Initialize the MCP server with required dependencies.
        
        Parameters
        ----------
        zk : Zettelkasten
            Zettelkasten instance needed for document-related tools
        smart_memory : SmartMemory
            SmartMemory instance needed for memory-related tools
        enable_unsafe_operations : bool, optional
            Flag to enable potentially unsafe operations like document creation, by default False
        """
        self.zk = zk
        self.smart_memory = smart_memory
        self.enable_unsafe_operations = enable_unsafe_operations
        self.tools = {}
        
        self._register_tools()
    
    def _register_tools(self) -> None:
        """
        Register the specific tools with appropriate dependencies.
        """
        # Register read-only tools
        self._register_tool(ReadZkDocument(self.zk))
        self._register_tool(FindExcerptsRelatedTo(self.zk))
        self._register_tool(FindZkDocumentsRelatedTo(self.zk))
        self._register_tool(RetrieveFromSmartMemory(self.smart_memory))
        self._register_tool(StoreInSmartMemory(self.smart_memory))
        
        # Register potentially unsafe tools if enabled
        if self.enable_unsafe_operations:
            self._register_tool(CreateOrOverwriteZkDocument(self.zk))
    
    def _register_tool(self, tool_instance: Any) -> None:
        """
        Register a tool instance with the server.
        
        Parameters
        ----------
        tool_instance : Any
            Instance of an LLMTool
        """
        descriptor = tool_instance.descriptor
        if "function" in descriptor:
            tool_name = descriptor["function"]["name"]
            self.tools[tool_name] = tool_instance
            logger.info("Registered tool", name=tool_name)
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get a list of available tools and their metadata in MCP format.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of tool descriptors in MCP format
        """
        return [tool.descriptor for tool in self.tools.values()]
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with the given parameters.
        
        Parameters
        ----------
        tool_name : str
            Name of the tool to execute
        parameters : Dict[str, Any]
            Parameters to pass to the tool
            
        Returns
        -------
        Dict[str, Any]
            Tool execution result
        """
        if tool_name not in self.tools:
            logger.error("Tool not found", tool_name=tool_name)
            return {"status": "error", "error": f"Tool '{tool_name}' not found"}
        
        logger.info("Executing tool", tool_name=tool_name, parameters=parameters)
        
        try:
            # Call the tool's run method with the parameters
            result = self.tools[tool_name].run(**parameters)
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error("Tool execution failed", 
                        tool_name=tool_name, 
                        error=str(e))
            return {"status": "error", "error": str(e)}
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an MCP request and return the response.
        
        Parameters
        ----------
        request : Dict[str, Any]
            MCP request containing tool name and parameters
            
        Returns
        -------
        Dict[str, Any]
            MCP response with result or error
        """
        if "type" not in request:
            return {"status": "error", "error": "Invalid request format: missing 'type'"}
        
        if request["type"] == "tool_call":
            if "tool" not in request or "parameters" not in request:
                return {"status": "error", "error": "Invalid tool_call request: missing 'tool' or 'parameters'"}
            
            tool_name = request["tool"]
            parameters = request["parameters"]
            
            return self.execute_tool(tool_name, parameters)
            
        elif request["type"] == "list_tools":
            return {
                "status": "success",
                "tools": self.get_available_tools()
            }
            
        else:
            return {"status": "error", "error": f"Unsupported request type: {request['type']}"}
    
    def handle_mcp_request(self, request_json: str) -> str:
        """
        Handle an MCP request in JSON format and return the response.
        
        Parameters
        ----------
        request_json : str
            JSON string containing the MCP request
            
        Returns
        -------
        str
            JSON string containing the MCP response
        """
        try:
            request = json.loads(request_json)
            response = self.process_request(request)
            return json.dumps(response)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request")
            return json.dumps({"status": "error", "error": "Invalid JSON"})
        except Exception as e:
            logger.error("Error handling MCP request", error=str(e))
            return json.dumps({"status": "error", "error": str(e)})


def create_mcp_server(
    zk: Zettelkasten, 
    smart_memory: SmartMemory,
    enable_unsafe_operations: bool = False
) -> MCPServer:
    """
    Helper function to create and configure an MCP server.
    
    Parameters
    ----------
    zk : Zettelkasten
        Zettelkasten instance for document-related tools
    smart_memory : SmartMemory
        SmartMemory instance for memory-related tools
    enable_unsafe_operations : bool, optional
        Flag to enable potentially unsafe operations like document creation, by default False
        
    Returns
    -------
    MCPServer
        Configured MCP server instance
    """
    return MCPServer(zk=zk, smart_memory=smart_memory, enable_unsafe_operations=enable_unsafe_operations)
