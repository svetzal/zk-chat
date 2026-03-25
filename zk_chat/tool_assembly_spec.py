"""
Tests for the build_agent_tools function.

Verifies the correct assembly of tools from injected services.
"""

from unittest.mock import Mock

import pytest
from mojentic.llm import LLMBroker
from mojentic.llm.gateways import OllamaGateway
from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic.llm.tools.date_resolver import ResolveDateTool

from zk_chat.config import Config
from zk_chat.console_service import RichConsoleService
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.services.document_service import DocumentService
from zk_chat.services.index_service import IndexService
from zk_chat.services.link_traversal_service import LinkTraversalService
from zk_chat.tool_assembly import build_agent_tools
from zk_chat.tools.analyze_image import AnalyzeImage
from zk_chat.tools.commit_changes import CommitChanges
from zk_chat.tools.create_or_overwrite_zk_document import CreateOrOverwriteZkDocument
from zk_chat.tools.delete_zk_document import DeleteZkDocument
from zk_chat.tools.find_backlinks import FindBacklinks
from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo
from zk_chat.tools.find_forward_links import FindForwardLinks
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo
from zk_chat.tools.git_gateway import GitGateway
from zk_chat.tools.list_zk_documents import ListZkDocuments
from zk_chat.tools.list_zk_images import ListZkImages
from zk_chat.tools.read_zk_document import ReadZkDocument
from zk_chat.tools.rename_zk_document import RenameZkDocument
from zk_chat.tools.resolve_wikilink import ResolveWikiLink
from zk_chat.tools.retrieve_from_smart_memory import RetrieveFromSmartMemory
from zk_chat.tools.store_in_smart_memory import StoreInSmartMemory
from zk_chat.tools.uncommitted_changes import UncommittedChanges

_EXPECTED_TOOL_COUNT = 18


@pytest.fixture
def mock_config():
    config = Mock(spec=Config)
    config.visual_model = "llama3.2-vision"
    config.vault = "/tmp/test-vault"
    return config


@pytest.fixture
def mock_gateway():
    return Mock(spec=OllamaGateway)


@pytest.fixture
def mock_llm(mock_gateway):
    return LLMBroker(model="test-model", gateway=mock_gateway)


@pytest.fixture
def tools(mock_config, mock_gateway, mock_llm):
    return build_agent_tools(
        config=mock_config,
        filesystem_gateway=Mock(spec=MarkdownFilesystemGateway),
        document_service=Mock(spec=DocumentService),
        index_service=Mock(spec=IndexService),
        link_traversal_service=Mock(spec=LinkTraversalService),
        llm=mock_llm,
        smart_memory=Mock(spec=SmartMemory),
        git_gateway=Mock(spec=GitGateway),
        gateway=mock_gateway,
        console_service=Mock(spec=RichConsoleService),
    )


class DescribeBuildAgentTools:
    """Tests for the build_agent_tools assembly function."""

    def should_return_a_list(self, tools):
        assert isinstance(tools, list)

    def should_return_expected_number_of_tools(self, tools):
        assert len(tools) == _EXPECTED_TOOL_COUNT

    class DescribeContextTools:
        def should_include_current_datetime_tool(self, tools):
            tool_types = [type(t) for t in tools]
            assert CurrentDateTimeTool in tool_types

        def should_include_resolve_date_tool(self, tools):
            tool_types = [type(t) for t in tools]
            assert ResolveDateTool in tool_types

    class DescribeDocumentTools:
        def should_include_read_zk_document(self, tools):
            tool_types = [type(t) for t in tools]
            assert ReadZkDocument in tool_types

        def should_include_list_zk_documents(self, tools):
            tool_types = [type(t) for t in tools]
            assert ListZkDocuments in tool_types

        def should_include_list_zk_images(self, tools):
            tool_types = [type(t) for t in tools]
            assert ListZkImages in tool_types

        def should_include_resolve_wikilink(self, tools):
            tool_types = [type(t) for t in tools]
            assert ResolveWikiLink in tool_types

        def should_include_find_excerpts_related_to(self, tools):
            tool_types = [type(t) for t in tools]
            assert FindExcerptsRelatedTo in tool_types

        def should_include_find_zk_documents_related_to(self, tools):
            tool_types = [type(t) for t in tools]
            assert FindZkDocumentsRelatedTo in tool_types

        def should_include_create_or_overwrite_zk_document(self, tools):
            tool_types = [type(t) for t in tools]
            assert CreateOrOverwriteZkDocument in tool_types

        def should_include_rename_zk_document(self, tools):
            tool_types = [type(t) for t in tools]
            assert RenameZkDocument in tool_types

        def should_include_delete_zk_document(self, tools):
            tool_types = [type(t) for t in tools]
            assert DeleteZkDocument in tool_types

    class DescribeGraphTools:
        def should_include_find_backlinks(self, tools):
            tool_types = [type(t) for t in tools]
            assert FindBacklinks in tool_types

        def should_include_find_forward_links(self, tools):
            tool_types = [type(t) for t in tools]
            assert FindForwardLinks in tool_types

    class DescribeMemoryTools:
        def should_include_store_in_smart_memory(self, tools):
            tool_types = [type(t) for t in tools]
            assert StoreInSmartMemory in tool_types

        def should_include_retrieve_from_smart_memory(self, tools):
            tool_types = [type(t) for t in tools]
            assert RetrieveFromSmartMemory in tool_types

    class DescribeVisualTools:
        def should_include_analyze_image(self, tools):
            tool_types = [type(t) for t in tools]
            assert AnalyzeImage in tool_types

    class DescribeGitTools:
        def should_include_uncommitted_changes(self, tools):
            tool_types = [type(t) for t in tools]
            assert UncommittedChanges in tool_types

        def should_include_commit_changes(self, tools):
            tool_types = [type(t) for t in tools]
            assert CommitChanges in tool_types
