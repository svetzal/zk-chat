from unittest.mock import Mock

import pytest

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.services.document_service import DocumentService
from zk_chat.tools.delete_zk_document import DeleteZkDocument


@pytest.fixture
def mock_filesystem():
    return Mock(spec=MarkdownFilesystemGateway)


@pytest.fixture
def delete_tool(mock_filesystem):
    return DeleteZkDocument(DocumentService(mock_filesystem))


def test_initialization(mock_filesystem):
    document_service = DocumentService(mock_filesystem)
    tool = DeleteZkDocument(document_service)

    assert isinstance(tool, DeleteZkDocument)
    assert tool.document_service is document_service


def test_delete_document_when_exists(delete_tool, mock_filesystem):
    relative_path = "test/path.md"
    mock_filesystem.path_exists.return_value = True

    result = delete_tool.run(relative_path=relative_path)

    # path_exists is called twice: once in tool.run() and once in DocumentService.delete_document()
    assert mock_filesystem.path_exists.call_count == 2
    mock_filesystem.delete_file.assert_called_once_with(relative_path)
    assert result == f"Document successfully deleted at {relative_path}"


def test_delete_document_when_not_exists(delete_tool, mock_filesystem):
    relative_path = "test/nonexistent.md"
    mock_filesystem.path_exists.return_value = False

    result = delete_tool.run(relative_path=relative_path)

    mock_filesystem.path_exists.assert_called_once_with(relative_path)
    mock_filesystem.delete_file.assert_not_called()
    assert result == f"Document not found at {relative_path}"


def test_delete_document_handles_exception(delete_tool, mock_filesystem):
    relative_path = "test/error.md"
    mock_filesystem.path_exists.return_value = True
    mock_filesystem.delete_file.side_effect = Exception("Test error")

    result = delete_tool.run(relative_path=relative_path)

    # path_exists is called twice: once in tool.run() and once in DocumentService.delete_document()
    assert mock_filesystem.path_exists.call_count == 2
    mock_filesystem.delete_file.assert_called_once_with(relative_path)
    assert result == f"Error deleting document at {relative_path}: Test error"


def test_descriptor_property(delete_tool):
    descriptor = delete_tool.descriptor

    assert descriptor["type"] == "function"
    assert descriptor["function"]["name"] == "delete_document"
    assert "description" in descriptor["function"]
    assert descriptor["function"]["parameters"]["type"] == "object"
    assert "relative_path" in descriptor["function"]["parameters"]["properties"]
    assert descriptor["function"]["parameters"]["required"] == ["relative_path"]
