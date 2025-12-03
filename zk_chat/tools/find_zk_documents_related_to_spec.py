import json

import pytest
from mojentic.llm.tools.llm_tool import LLMTool
from pytest_mock import MockerFixture
from unittest.mock import Mock

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.models import ZkDocument, ZkQueryDocumentResult, QueryResult, VectorDocumentForStorage
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo
from zk_chat.vector_database import VectorDatabase
from zk_chat.zettelkasten import Zettelkasten


@pytest.fixture
def mock_filesystem():
    return Mock(spec=MarkdownFilesystemGateway)


@pytest.fixture
def mock_excerpts_db():
    return Mock(spec=VectorDatabase)


@pytest.fixture
def mock_documents_db():
    return Mock(spec=VectorDatabase)


@pytest.fixture
def mock_tokenizer_gateway():
    return Mock()


@pytest.fixture
def mock_zk(mocker: MockerFixture, mock_filesystem, mock_excerpts_db, mock_documents_db, mock_tokenizer_gateway) -> Zettelkasten:
    mock = mocker.Mock(spec=Zettelkasten)
    mock.filesystem_gateway = mock_filesystem
    mock.excerpts_db = mock_excerpts_db
    mock.documents_db = mock_documents_db
    mock.tokenizer_gateway = mock_tokenizer_gateway
    return mock


@pytest.fixture
def tool(mock_zk: Zettelkasten, mock_filesystem) -> LLMTool:
    return FindZkDocumentsRelatedTo(mock_zk)


def test_run_returns_document_ids_and_titles(
        tool: FindZkDocumentsRelatedTo,
        mock_zk: Zettelkasten,
        mock_documents_db,
        mock_filesystem,
):
    # Mock the vector database query result
    mock_documents_db.query.return_value = [
        QueryResult(
            document=VectorDocumentForStorage(
                id="doc1",
                content="First Document",
                metadata={}
            ),
            distance=0.8
        ),
        QueryResult(
            document=VectorDocumentForStorage(
                id="doc2",
                content="Second Document",
                metadata={}
            ),
            distance=0.7
        )
    ]
    # Mock the filesystem to return full documents
    mock_filesystem.read_markdown.side_effect = [
        ({}, "First Document"),
        ({}, "Second Document")
    ]

    result = tool.run("test query")
    parsed = json.loads(result)

    assert len(parsed) == 2
    assert parsed[0]["distance"] == 0.8
    assert parsed[0]["document"]["relative_path"] == "doc1"
    assert parsed[1]["distance"] == 0.7
    assert parsed[1]["document"]["relative_path"] == "doc2"
