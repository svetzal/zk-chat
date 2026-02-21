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
    # Set up the filesystem mock defaults
    mock_filesystem.get_directory_path.return_value = ""
    mock_filesystem.path_exists.return_value = True
    return CreateOrOverwriteZkDocument(DocumentService(mock_filesystem))


def test_write_document_happy_path(write_tool, mock_filesystem):
    title = "Path"
    metadata = {"title": "Test Document"}
    content = "# Test Content"

    result = write_tool.run(title=title, metadata=metadata, content=content)

    assert f"Successfully wrote to {title}.md" in result
    mock_filesystem.write_markdown.assert_called_once()
    call_args = mock_filesystem.write_markdown.call_args[0]
    assert call_args[0] == f"{title}.md"  # relative_path
    expected_metadata = metadata.copy()
    expected_metadata["reviewed"] = False
    assert call_args[1] == expected_metadata  # metadata
    assert call_args[2] == content  # content


def test_write_document_with_none_metadata(write_tool, mock_filesystem):
    title = "Path"
    metadata = None
    content = "# Test Content"

    result = write_tool.run(title=title, metadata=metadata, content=content)

    assert f"Successfully wrote to {title}.md" in result
    mock_filesystem.write_markdown.assert_called_once()
    call_args = mock_filesystem.write_markdown.call_args[0]
    assert call_args[0] == f"{title}.md"  # relative_path
    expected_metadata = {"reviewed": False}
    assert call_args[1] == expected_metadata  # metadata
    assert call_args[2] == content  # content


def test_write_document_with_non_dict_metadata(write_tool, mock_filesystem):
    title = "Path"
    metadata = "This is not a dictionary"
    content = "# Test Content"

    result = write_tool.run(title=title, metadata=metadata, content=content)

    assert f"Successfully wrote to {title}.md" in result
    mock_filesystem.write_markdown.assert_called_once()
    call_args = mock_filesystem.write_markdown.call_args[0]
    assert call_args[0] == f"{title}.md"  # relative_path
    expected_metadata = {"reviewed": False}
    assert call_args[1] == expected_metadata  # metadata
    assert call_args[2] == content  # content
