from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.models import ZkDocument
from zk_chat.tools.read_zk_document import ReadZkDocument


@pytest.fixture
def mock_filesystem():
    return Mock(spec=MarkdownFilesystemGateway)


@pytest.fixture
def mock_zk(mocker: MockerFixture, mock_filesystem):
    mock = mocker.Mock()
    mock.filesystem_gateway = mock_filesystem
    return mock


@pytest.fixture
def read_tool(mock_zk):
    return ReadZkDocument(mock_zk)


def test_read_document_when_exists(read_tool, mock_zk, mock_filesystem):
    relative_path = "test/path.md"
    mock_filesystem.path_exists.return_value = True
    mock_filesystem.read_markdown.return_value = ({"title": "Test"}, "# Test Content")

    result = read_tool.run(relative_path=relative_path)

    mock_filesystem.path_exists.assert_called_once_with(relative_path)
    mock_filesystem.read_markdown.assert_called_once_with(relative_path)
    expected_result = ZkDocument(relative_path=relative_path, metadata={"title": "Test"},
                                 content="# Test Content")
    assert result == expected_result.model_dump_json()


def test_read_document_when_not_exists(read_tool, mock_zk, mock_filesystem):
    relative_path = "test/nonexistent.md"
    mock_filesystem.path_exists.return_value = False

    result = read_tool.run(relative_path=relative_path)

    mock_filesystem.path_exists.assert_called_once_with(relative_path)
    mock_filesystem.read_markdown.assert_not_called()
    assert result == f"Document not found at {relative_path}"
