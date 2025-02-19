import pytest
from pytest_mock import MockerFixture

from zk_chat.models import ZkDocument
from zk_chat.tools.write_zk_document import WriteZkDocument


@pytest.fixture
def mock_zk(mocker: MockerFixture):
    return mocker.Mock()


@pytest.fixture
def write_tool(mock_zk):
    return WriteZkDocument(mock_zk)


def test_write_document_happy_path(write_tool, mock_zk):
    relative_path = "test/path.md"
    metadata = {"title": "Test Document"}
    content = "# Test Content"
    
    result = write_tool.run(relative_path=relative_path, metadata=metadata, content=content)
    
    assert result == f"Successfully wrote to {relative_path}"
    mock_zk.write_zk_document.assert_called_once()
    written_document = mock_zk.write_zk_document.call_args[0][0]
    assert isinstance(written_document, ZkDocument)
    assert written_document.relative_path == relative_path
    assert written_document.metadata == metadata
    assert written_document.content == content
