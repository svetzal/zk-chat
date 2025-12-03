import json

import pytest
from pytest_mock import MockerFixture
from unittest.mock import Mock

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.models import ZkDocumentExcerpt, ZkQueryExcerptResult, QueryResult, VectorDocumentForStorage
from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo
from zk_chat.vector_database import VectorDatabase


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
def mock_zk(mocker: MockerFixture, mock_filesystem, mock_excerpts_db, mock_documents_db, mock_tokenizer_gateway):
    mock = mocker.Mock()
    mock.filesystem_gateway = mock_filesystem
    mock.excerpts_db = mock_excerpts_db
    mock.documents_db = mock_documents_db
    mock.tokenizer_gateway = mock_tokenizer_gateway
    return mock


@pytest.fixture
def find_excerpts_tool(mock_zk, mock_excerpts_db):
    return FindExcerptsRelatedTo(mock_zk)


def test_find_excerpts_related_to(find_excerpts_tool, mock_zk, mock_excerpts_db):
    query = "test query"
    mock_results = [
        QueryResult(
            document=VectorDocumentForStorage(
                id="doc1_0",
                content="Sample text 1",
                metadata={"id": "doc1", "title": "Test Doc 1"}
            ),
            distance=0.1
        ),
        QueryResult(
            document=VectorDocumentForStorage(
                id="doc2_0",
                content="Sample text 2",
                metadata={"id": "doc2", "title": "Test Doc 2"}
            ),
            distance=0.2
        )
    ]
    mock_excerpts_db.query.return_value = mock_results

    result = find_excerpts_tool.run(query)

    mock_excerpts_db.query.assert_called_once()
    parsed_result = json.loads(result)
    assert len(parsed_result) == 2
    assert parsed_result[0]["excerpt"]["document_id"] == "doc1"
    assert parsed_result[0]["excerpt"]["document_title"] == "Test Doc 1"
    assert parsed_result[1]["excerpt"]["document_id"] == "doc2"
