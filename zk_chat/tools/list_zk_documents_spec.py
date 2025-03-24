import pytest
from pytest_mock import MockerFixture
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.models import ZkDocument
from zk_chat.tools.list_zk_documents import ListZkDocuments
from zk_chat.zettelkasten import Zettelkasten


@pytest.fixture
def mock_zk(mocker: MockerFixture) -> Zettelkasten:
    return mocker.Mock(spec=Zettelkasten)


@pytest.fixture
def tool(mock_zk: Zettelkasten) -> LLMTool:
    return ListZkDocuments(mock_zk)


def test_run_returns_list_of_document_titles(
    tool: ListZkDocuments,
    mock_zk: Zettelkasten,
):
    # Create mock documents
    documents = [
        ZkDocument(
            relative_path="doc1.md",
            content="First Document Content",
            metadata={},
        ),
        ZkDocument(
            relative_path="doc2.md",
            content="Second Document Content",
            metadata={},
        ),
        ZkDocument(
            relative_path="doc3.md",
            content="Third Document Content",
            metadata={},
        )
    ]

    # Set up the mock to return the documents when iterate_documents is called
    mock_zk.iterate_documents.return_value = documents

    # Call the tool's run method
    result = tool.run()

    # Verify the result contains the titles of the documents
    # The title property of ZkDocument returns the filename without extension
    expected = "doc1.md\ndoc2.md\ndoc3.md"
    assert result == expected
