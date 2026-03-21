"""
Tests for the ResolveWikiLink tool.
"""

from unittest.mock import Mock

import pytest

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.tools.resolve_wikilink import ResolveWikiLink


class DescribeResolveWikiLink:
    """Tests for the ResolveWikiLink LLM tool."""

    @pytest.fixture
    def mock_filesystem(self):
        return Mock(spec=MarkdownFilesystemGateway)

    @pytest.fixture
    def resolve_tool(self, mock_filesystem):
        return ResolveWikiLink(mock_filesystem)

    def should_return_relative_path_when_wikilink_resolves(self, resolve_tool, mock_filesystem):
        mock_filesystem.resolve_wikilink.return_value = "notes/test-note.md"

        result = resolve_tool.run("[[Test Note]]")

        assert result == "relative_path: notes/test-note.md"

    def should_return_error_message_when_wikilink_not_found(self, resolve_tool, mock_filesystem):
        mock_filesystem.resolve_wikilink.side_effect = ValueError("Not found")

        result = resolve_tool.run("[[Nonexistent Note]]")

        assert "no document currently present" in result

    def should_have_correct_descriptor_name(self, resolve_tool):
        assert resolve_tool.descriptor["function"]["name"] == "resolve_wikilink"

    def should_require_wikilink_parameter_in_descriptor(self, resolve_tool):
        assert "wikilink" in resolve_tool.descriptor["function"]["parameters"]["required"]
