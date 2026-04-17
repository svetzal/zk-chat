import pytest

from zk_chat.services.document_service import DocumentService
from zk_chat.tools.list_zk_documents import ListZkDocuments


@pytest.fixture
def tool(mock_filesystem, mock_console_service):
    return ListZkDocuments(DocumentService(mock_filesystem), mock_console_service)


class DescribeListZkDocuments:
    """Tests for the ListZkDocuments tool."""

    def should_return_newline_separated_document_paths(self, tool, mock_filesystem):
        mock_filesystem.iterate_markdown_files.return_value = ["doc1.md", "doc2.md", "doc3.md"]
        mock_filesystem.read_markdown.side_effect = [
            ({}, "First Document Content"),
            ({}, "Second Document Content"),
            ({}, "Third Document Content"),
        ]

        result = tool.run()

        expected = "doc1.md\ndoc2.md\ndoc3.md"
        assert result == expected
