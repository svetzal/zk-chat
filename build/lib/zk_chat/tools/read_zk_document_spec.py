import pytest
from pytest_mock import MockerFixture

from zk_chat.models import ZkDocument
from zk_chat.tools.read_zk_document import ReadZkDocument


@pytest.fixture
def mock_zk(mocker: MockerFixture):
    return mocker.Mock()


@pytest.fixture
def read_tool(mock_zk):
    return ReadZkDocument(mock_zk)


def test_read_document_when_exists(read_tool, mock_zk):
    relative_path = "test/path.md"
    mock_zk.document_exists.return_value = True
    expected_result = ZkDocument(relative_path=relative_path, metadata={"title": "Test"},
                      content="# Test Content")
    mock_zk.read_document.return_value = expected_result

    result = read_tool.run(relative_path=relative_path)

    mock_zk.document_exists.assert_called_once_with(relative_path)
    mock_zk.read_document.assert_called_once_with(relative_path)
    assert result == expected_result.model_dump_json()


def test_read_document_when_not_exists(read_tool, mock_zk):
    relative_path = "test/nonexistent.md"
    mock_zk.document_exists.return_value = False

    result = read_tool.run(relative_path=relative_path)

    mock_zk.document_exists.assert_called_once_with(relative_path)
    mock_zk.read_document.assert_not_called()
    assert result == f"Document not found at {relative_path}"
