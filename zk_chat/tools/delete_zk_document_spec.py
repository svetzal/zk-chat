import pytest
from pytest_mock import MockerFixture

from zk_chat.tools.delete_zk_document import DeleteZkDocument
from zk_chat.zettelkasten import Zettelkasten


@pytest.fixture
def mock_zk(mocker: MockerFixture):
    return mocker.Mock(spec=Zettelkasten)


@pytest.fixture
def delete_tool(mock_zk):
    return DeleteZkDocument(mock_zk)


def test_initialization(mock_zk):
    tool = DeleteZkDocument(mock_zk)
    
    assert isinstance(tool, DeleteZkDocument)
    assert tool.zk == mock_zk


def test_delete_document_when_exists(delete_tool, mock_zk):
    relative_path = "test/path.md"
    mock_zk.document_exists.return_value = True
    
    result = delete_tool.run(relative_path=relative_path)
    
    mock_zk.document_exists.assert_called_once_with(relative_path)
    mock_zk.delete_document.assert_called_once_with(relative_path)
    assert result == f"Document successfully deleted at {relative_path}"


def test_delete_document_when_not_exists(delete_tool, mock_zk):
    relative_path = "test/nonexistent.md"
    mock_zk.document_exists.return_value = False
    
    result = delete_tool.run(relative_path=relative_path)
    
    mock_zk.document_exists.assert_called_once_with(relative_path)
    mock_zk.delete_document.assert_not_called()
    assert result == f"Document not found at {relative_path}"


def test_delete_document_handles_exception(delete_tool, mock_zk):
    relative_path = "test/error.md"
    mock_zk.document_exists.return_value = True
    mock_zk.delete_document.side_effect = Exception("Test error")
    
    result = delete_tool.run(relative_path=relative_path)
    
    mock_zk.document_exists.assert_called_once_with(relative_path)
    mock_zk.delete_document.assert_called_once_with(relative_path)
    assert result == f"Error deleting document at {relative_path}: Test error"


def test_descriptor_property(delete_tool):
    descriptor = delete_tool.descriptor
    
    assert descriptor["type"] == "function"
    assert descriptor["function"]["name"] == "delete_document"
    assert "description" in descriptor["function"]
    assert descriptor["function"]["parameters"]["type"] == "object"
    assert "relative_path" in descriptor["function"]["parameters"]["properties"]
    assert descriptor["function"]["parameters"]["required"] == ["relative_path"]