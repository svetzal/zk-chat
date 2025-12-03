import pytest
from mojentic.llm.tools.llm_tool import LLMTool
from pytest_mock import MockerFixture
from unittest.mock import Mock

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.models import ZkDocument
from zk_chat.tools.list_zk_documents import ListZkDocuments
from zk_chat.zettelkasten import Zettelkasten


@pytest.fixture
def mock_filesystem():
    return Mock(spec=MarkdownFilesystemGateway)


@pytest.fixture
def mock_zk(mocker: MockerFixture, mock_filesystem) -> Zettelkasten:
    mock = mocker.Mock(spec=Zettelkasten)
    mock.filesystem_gateway = mock_filesystem
    return mock


@pytest.fixture
def tool(mock_zk: Zettelkasten) -> LLMTool:
    return ListZkDocuments(mock_zk)


def test_run_returns_list_of_document_titles(
        tool: ListZkDocuments,
        mock_zk: Zettelkasten,
        mock_filesystem,
):
    # Set up the mock filesystem to return document paths and metadata/content
    mock_filesystem.iterate_markdown_files.return_value = ["doc1.md", "doc2.md", "doc3.md"]
    mock_filesystem.read_markdown.side_effect = [
        ({}, "First Document Content"),
        ({}, "Second Document Content"),
        ({}, "Third Document Content"),
    ]

    # Call the tool's run method
    result = tool.run()

    # Verify the result contains the titles of the documents
    # The title property of ZkDocument returns the filename without extension
    expected = "doc1.md\ndoc2.md\ndoc3.md"
    assert result == expected
