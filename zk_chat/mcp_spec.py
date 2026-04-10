"""
Tests for the MCPServer class.
"""

import json
from unittest.mock import Mock

import pytest
from mojentic.llm.gateways import OllamaGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.console_service import ConsoleGateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.mcp import MCPServer, create_mcp_server
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.services.document_service import DocumentService
from zk_chat.services.index_service import IndexService
from zk_chat.vector_database import VectorDatabase


class _StubTool(LLMTool):
    """Minimal concrete LLMTool implementation for use in tests."""

    def __init__(self, return_value=None, side_effect=None):
        super().__init__()
        self._return_value = return_value
        self._side_effect = side_effect
        self.call_args = None

    def run(self, **kwargs):
        self.call_args = kwargs
        if self._side_effect is not None:
            raise self._side_effect
        return self._return_value

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {"name": "stub_tool", "description": "Stub tool for testing", "parameters": {}},
        }


@pytest.fixture
def mock_filesystem():
    return Mock(spec=MarkdownFilesystemGateway)


@pytest.fixture
def mock_model_gateway():
    gateway = Mock(spec=OllamaGateway)
    gateway.calculate_embeddings.return_value = [0.1, 0.2, 0.3]
    return gateway


@pytest.fixture
def document_service(mock_filesystem):
    return DocumentService(mock_filesystem)


@pytest.fixture
def index_service(mock_filesystem, mock_model_gateway):
    return IndexService(
        tokenizer_gateway=Mock(spec=TokenizerGateway),
        excerpts_db=VectorDatabase(Mock(spec=ChromaGateway), mock_model_gateway, ZkCollectionName.EXCERPTS),
        documents_db=VectorDatabase(Mock(spec=ChromaGateway), mock_model_gateway, ZkCollectionName.DOCUMENTS),
        filesystem_gateway=mock_filesystem,
    )


@pytest.fixture
def smart_memory(mock_model_gateway):
    return SmartMemory(Mock(spec=ChromaGateway), mock_model_gateway)


@pytest.fixture
def mock_console_service():
    return Mock(spec=ConsoleGateway)


@pytest.fixture
def server(document_service, index_service, smart_memory, mock_console_service):
    return MCPServer(
        document_service=document_service,
        index_service=index_service,
        smart_memory=smart_memory,
        console_service=mock_console_service,
    )


@pytest.fixture
def unsafe_server(document_service, index_service, smart_memory, mock_console_service):
    return MCPServer(
        document_service=document_service,
        index_service=index_service,
        smart_memory=smart_memory,
        enable_unsafe_operations=True,
        console_service=mock_console_service,
    )


class DescribeMCPServer:
    """Tests for MCPServer initialization and configuration."""

    class DescribeInit:
        def should_be_instantiated_with_required_dependencies(
            self, document_service, index_service, smart_memory, mock_console_service
        ):
            srv = MCPServer(
                document_service=document_service,
                index_service=index_service,
                smart_memory=smart_memory,
                console_service=mock_console_service,
            )

            assert isinstance(srv, MCPServer)

        def should_register_five_read_only_tools_by_default(self, server):
            assert len(server.tools) == 5

        def should_register_six_tools_when_unsafe_operations_enabled(self, unsafe_server):
            assert len(unsafe_server.tools) == 6

        def should_include_read_document_tool(self, server):
            assert "read_document" in server.tools

        def should_include_find_excerpts_tool(self, server):
            assert "find_excerpts" in server.tools

        def should_include_find_documents_tool(self, server):
            assert "find_documents" in server.tools

        def should_include_retrieve_from_memory_tool(self, server):
            assert "retrieve_from_smart_memory" in server.tools

        def should_include_store_in_memory_tool(self, server):
            assert "store_in_smart_memory" in server.tools

        def should_not_include_create_document_tool_when_safe_mode(self, server):
            assert "create_or_overwrite_zk_document" not in server.tools

        def should_include_create_document_tool_when_unsafe_enabled(self, unsafe_server):
            assert "create_or_overwrite_document" in unsafe_server.tools

    class DescribeGetAvailableTools:
        def should_return_list_of_tool_descriptors(self, server):
            tools = server.get_available_tools()

            assert isinstance(tools, list)
            assert len(tools) == 5

        def should_return_dicts_with_function_key(self, server):
            tools = server.get_available_tools()

            for tool in tools:
                assert "function" in tool

        def should_return_six_tools_when_unsafe_enabled(self, unsafe_server):
            tools = unsafe_server.get_available_tools()

            assert len(tools) == 6

    class DescribeExecuteTool:
        def should_return_error_for_unknown_tool(self, server):
            result = server.execute_tool("nonexistent_tool", {})

            assert result["status"] == "error"
            assert "nonexistent_tool" in result["error"]

        def should_return_success_when_tool_executes(self, server):
            stub_tool = _StubTool(return_value="tool result")
            server.tools["test_tool"] = stub_tool

            result = server.execute_tool("test_tool", {"key": "value"})

            assert result["status"] == "success"
            assert result["result"] == "tool result"
            assert stub_tool.call_args == {"key": "value"}

        def should_return_error_when_tool_raises_exception(self, server):
            stub_tool = _StubTool(side_effect=ValueError("something broke"))
            server.tools["failing_tool"] = stub_tool

            result = server.execute_tool("failing_tool", {})

            assert result["status"] == "error"
            assert "something broke" in result["error"]

    class DescribeProcessRequest:
        def should_return_error_when_type_missing_from_request(self, server):
            result = server.process_request({"tool": "read_document"})

            assert result["status"] == "error"
            assert "type" in result["error"]

        def should_return_tool_list_for_list_tools_request(self, server):
            result = server.process_request({"type": "list_tools"})

            assert result["status"] == "success"
            assert "tools" in result
            assert len(result["tools"]) == 5

        def should_return_error_for_unsupported_request_type(self, server):
            result = server.process_request({"type": "unknown_type"})

            assert result["status"] == "error"
            assert "unknown_type" in result["error"]

        def should_return_error_for_tool_call_missing_tool_key(self, server):
            result = server.process_request({"type": "tool_call", "parameters": {}})

            assert result["status"] == "error"
            assert "tool" in result["error"] or "parameters" in result["error"]

        def should_return_error_for_tool_call_missing_parameters_key(self, server):
            result = server.process_request({"type": "tool_call", "tool": "read_document"})

            assert result["status"] == "error"

        def should_execute_tool_for_valid_tool_call_request(self, server):
            stub_tool = _StubTool(return_value="result data")
            server.tools["my_tool"] = stub_tool

            result = server.process_request({"type": "tool_call", "tool": "my_tool", "parameters": {}})

            assert result["status"] == "success"
            assert result["result"] == "result data"

    class DescribeHandleMcpRequest:
        def should_parse_json_and_return_json_response(self, server):
            request_json = json.dumps({"type": "list_tools"})

            response_json = server.handle_mcp_request(request_json)
            response = json.loads(response_json)

            assert response["status"] == "success"
            assert "tools" in response

        def should_return_error_json_for_invalid_json(self, server):
            response_json = server.handle_mcp_request("{ not valid json }")
            response = json.loads(response_json)

            assert response["status"] == "error"
            assert "Invalid JSON" in response["error"]

        def should_return_string_response(self, server):
            request_json = json.dumps({"type": "list_tools"})

            response = server.handle_mcp_request(request_json)

            assert isinstance(response, str)


class DescribeCreateMcpServer:
    def should_return_mcp_server_instance(self, document_service, index_service, smart_memory):
        srv = create_mcp_server(
            document_service=document_service,
            index_service=index_service,
            smart_memory=smart_memory,
        )

        assert isinstance(srv, MCPServer)

    def should_create_server_with_unsafe_operations_disabled_by_default(
        self, document_service, index_service, smart_memory
    ):
        srv = create_mcp_server(
            document_service=document_service,
            index_service=index_service,
            smart_memory=smart_memory,
        )

        assert srv.enable_unsafe_operations is False
        assert len(srv.tools) == 5
