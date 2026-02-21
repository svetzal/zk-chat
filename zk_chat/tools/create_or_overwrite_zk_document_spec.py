from unittest.mock import Mock

import pytest

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.services.document_service import DocumentService
from zk_chat.tools.create_or_overwrite_zk_document import CreateOrOverwriteZkDocument


@pytest.fixture
def mock_filesystem():
    return Mock(spec=MarkdownFilesystemGateway)


@pytest.fixture
def write_tool(mock_filesystem):
    mock_filesystem.get_directory_path.return_value = ""
    mock_filesystem.path_exists.return_value = True
    return CreateOrOverwriteZkDocument(DocumentService(mock_filesystem))


class DescribeCreateOrOverwriteZkDocument:
    """Tests for the CreateOrOverwriteZkDocument tool."""

    def should_write_document_with_dict_metadata(self, write_tool, mock_filesystem):
        title = "Path"
        metadata = {"title": "Test Document"}
        content = "# Test Content"

        result = write_tool.run(title=title, metadata=metadata, content=content)

        assert f"Successfully wrote to {title}.md" in result
        mock_filesystem.write_markdown.assert_called_once()
        call_args = mock_filesystem.write_markdown.call_args[0]
        assert call_args[0] == f"{title}.md"
        expected_metadata = metadata.copy()
        expected_metadata["reviewed"] = False
        assert call_args[1] == expected_metadata
        assert call_args[2] == content

    def should_write_document_with_default_metadata_when_none_provided(self, write_tool, mock_filesystem):
        title = "Path"
        content = "# Test Content"

        result = write_tool.run(title=title, metadata=None, content=content)

        assert f"Successfully wrote to {title}.md" in result
        mock_filesystem.write_markdown.assert_called_once()
        call_args = mock_filesystem.write_markdown.call_args[0]
        assert call_args[0] == f"{title}.md"
        assert call_args[1] == {"reviewed": False}
        assert call_args[2] == content

    def should_write_document_with_default_metadata_when_non_dict_provided(self, write_tool, mock_filesystem):
        title = "Path"
        content = "# Test Content"

        result = write_tool.run(title=title, metadata="This is not a dictionary", content=content)

        assert f"Successfully wrote to {title}.md" in result
        mock_filesystem.write_markdown.assert_called_once()
        call_args = mock_filesystem.write_markdown.call_args[0]
        assert call_args[0] == f"{title}.md"
        assert call_args[1] == {"reviewed": False}
        assert call_args[2] == content
