from unittest.mock import Mock

import pytest

from zk_chat.console_service import RichConsoleService
from zk_chat.markdown.markdown_filesystem_gateway import WikiLink
from zk_chat.models import ZkDocument
from zk_chat.tools.extract_wikilinks_from_document import ExtractWikilinksFromDocument
from zk_chat.services.link_traversal_service import WikiLinkReference
from zk_chat.zettelkasten import Zettelkasten


class DescribeExtractWikilinksFromDocument:
    """
    Tests for the ExtractWikilinksFromDocument tool which extracts wikilinks from document content.
    """

    @pytest.fixture
    def mock_zk(self):
        mock = Mock(spec=Zettelkasten)
        mock.filesystem_gateway = Mock()
        return mock

    @pytest.fixture
    def mock_console_service(self):
        return Mock(spec=RichConsoleService)

    @pytest.fixture
    def extract_tool(self, mock_zk, mock_console_service):
        return ExtractWikilinksFromDocument(mock_zk, mock_console_service)

    def should_be_instantiated_with_zettelkasten_and_console_service(self, mock_zk, mock_console_service):
        tool = ExtractWikilinksFromDocument(mock_zk, mock_console_service)

        assert isinstance(tool, ExtractWikilinksFromDocument)
        assert tool.zk == mock_zk
        assert tool.console_service == mock_console_service

    def should_use_default_console_service_when_none_provided(self, mock_zk):
        tool = ExtractWikilinksFromDocument(mock_zk)

        assert isinstance(tool, ExtractWikilinksFromDocument)
        assert tool.zk == mock_zk
        assert isinstance(tool.console_service, RichConsoleService)

    def should_return_error_message_when_document_does_not_exist(self, extract_tool, mock_zk):
        test_path = "nonexistent/document.md"
        mock_zk.document_exists.return_value = False

        result = extract_tool.run(test_path)

        mock_zk.document_exists.assert_called_once_with(test_path)
        assert result == f"Document not found at {test_path}"

    def should_extract_simple_wikilinks_from_document_content(self, extract_tool, mock_zk):
        test_path = "test/document.md"
        test_content = "This is a document with [[Link One]] and [[Link Two]] references."

        mock_zk.document_exists.return_value = True
        # Mock the filesystem gateway that the LinkTraversalService uses
        mock_zk.filesystem_gateway.path_exists.return_value = True
        mock_zk.filesystem_gateway.read_markdown.return_value = ({}, test_content)

        result = extract_tool.run(test_path)

        mock_zk.document_exists.assert_called_once_with(test_path)
        assert "Link One" in result
        assert "Link Two" in result

    def should_extract_wikilinks_with_captions(self, extract_tool, mock_zk):
        test_path = "test/document.md"
        test_content = "Reference to [[Document Title|Display Text]] here."

        mock_zk.document_exists.return_value = True
        # Mock the filesystem gateway that the LinkTraversalService uses
        mock_zk.filesystem_gateway.path_exists.return_value = True
        mock_zk.filesystem_gateway.read_markdown.return_value = ({}, test_content)

        result = extract_tool.run(test_path)

        assert "Document Title" in result
        assert "Display Text" in result

    def should_extract_wikilinks_from_multiple_lines(self, extract_tool, mock_zk):
        test_path = "test/document.md"
        test_content = """Line 1 has [[First Link]]
Line 2 has [[Second Link]] and [[Third Link]]
Line 3 has no links
Line 4 has [[Fourth Link|With Caption]]"""

        mock_zk.document_exists.return_value = True
        # Mock the filesystem gateway that the LinkTraversalService uses
        mock_zk.filesystem_gateway.path_exists.return_value = True
        mock_zk.filesystem_gateway.read_markdown.return_value = ({}, test_content)

        result = extract_tool.run(test_path)

        assert "First Link" in result
        assert "Second Link" in result
        assert "Third Link" in result
        assert "Fourth Link" in result
        assert "With Caption" in result

    def should_handle_document_with_no_wikilinks(self, extract_tool, mock_zk):
        test_path = "test/document.md"
        test_content = "This document has no wikilinks at all."

        mock_zk.document_exists.return_value = True
        # Mock the filesystem gateway that the LinkTraversalService uses
        mock_zk.filesystem_gateway.path_exists.return_value = True
        mock_zk.filesystem_gateway.read_markdown.return_value = ({}, test_content)

        result = extract_tool.run(test_path)

        assert result == "[]"

    def should_handle_empty_document(self, extract_tool, mock_zk):
        test_path = "test/empty.md"
        test_content = ""

        mock_zk.document_exists.return_value = True
        # Mock the filesystem gateway that the LinkTraversalService uses
        mock_zk.filesystem_gateway.path_exists.return_value = True
        mock_zk.filesystem_gateway.read_markdown.return_value = ({}, test_content)

        result = extract_tool.run(test_path)

        assert result == "[]"

    def should_extract_wikilinks_with_line_numbers_and_context(self, extract_tool, mock_zk):
        test_path = "test/document.md"
        test_content = """First line
Second line with [[Test Link]]
Third line"""

        mock_zk.document_exists.return_value = True
        # Mock the filesystem gateway that the LinkTraversalService uses
        mock_zk.filesystem_gateway.path_exists.return_value = True
        mock_zk.filesystem_gateway.read_markdown.return_value = ({}, test_content)

        result = extract_tool.run(test_path)

        # Should contain line number and context information
        assert "line_number" in result
        assert "context_snippet" in result
        assert "Test Link" in result

    def should_skip_malformed_wikilinks(self, extract_tool, mock_zk):
        test_path = "test/document.md"
        test_content = "Valid: [[Good Link]] Invalid: [[Bad Link] Missing bracket"

        mock_zk.document_exists.return_value = True
        # Mock the filesystem gateway that the LinkTraversalService uses
        mock_zk.filesystem_gateway.path_exists.return_value = True
        mock_zk.filesystem_gateway.read_markdown.return_value = ({}, test_content)

        result = extract_tool.run(test_path)

        # Check that only one wikilink was extracted (the valid one)
        assert "Good Link" in result
        # The malformed wikilink should not be parsed as a wikilink object
        # (it may appear in context, but shouldn't have its own wikilink entry)
        assert "'title': 'Bad Link'" not in result

    def should_handle_multiple_wikilinks_on_same_line(self, extract_tool, mock_zk):
        test_path = "test/document.md"
        test_content = "Multiple links: [[First]] and [[Second]] and [[Third]]"

        mock_zk.document_exists.return_value = True
        # Mock the filesystem gateway that the LinkTraversalService uses
        mock_zk.filesystem_gateway.path_exists.return_value = True
        mock_zk.filesystem_gateway.read_markdown.return_value = ({}, test_content)

        result = extract_tool.run(test_path)

        # Should find all three wikilinks
        assert "First" in result
        assert "Second" in result
        assert "Third" in result

    def should_have_correct_descriptor_for_llm_integration(self, extract_tool):
        descriptor = extract_tool.descriptor

        assert descriptor["type"] == "function"
        function_def = descriptor["function"]
        assert function_def["name"] == "extract_wikilinks_from_document"
        assert "extract all wikilinks" in function_def["description"].lower()

        params = function_def["parameters"]
        assert params["type"] == "object"
        assert "relative_path" in params["properties"]
        assert params["required"] == ["relative_path"]