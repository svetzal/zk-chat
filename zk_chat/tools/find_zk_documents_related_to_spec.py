import json
from unittest.mock import Mock

import pytest
from mojentic.llm.gateways import OllamaGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.console_service import ConsoleGateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.models import ZkDocument, ZkQueryDocumentResult
from zk_chat.services.index_service import IndexService
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo
from zk_chat.tools.tool_helpers import format_model_results
from zk_chat.vector_database import VectorDatabase


def _make_index_service(chroma_excerpts=None, chroma_documents=None, filesystem=None):
    """Build a real IndexService with gateway mocks."""
    gateway = Mock(spec=OllamaGateway)
    gateway.calculate_embeddings.return_value = [0.1, 0.2, 0.3]

    if chroma_excerpts is None:
        chroma_excerpts = Mock(spec=ChromaGateway)
    if chroma_documents is None:
        chroma_documents = Mock(spec=ChromaGateway)
    if filesystem is None:
        filesystem = Mock(spec=MarkdownFilesystemGateway)

    return IndexService(
        tokenizer_gateway=Mock(spec=TokenizerGateway),
        excerpts_db=VectorDatabase(chroma_excerpts, gateway, ZkCollectionName.EXCERPTS),
        documents_db=VectorDatabase(chroma_documents, gateway, ZkCollectionName.DOCUMENTS),
        filesystem_gateway=filesystem,
    )


@pytest.fixture
def mock_console_service():
    return Mock(spec=ConsoleGateway)


@pytest.fixture
def mock_chroma_documents():
    return Mock(spec=ChromaGateway)


@pytest.fixture
def mock_filesystem():
    return Mock(spec=MarkdownFilesystemGateway)


@pytest.fixture
def index_service(mock_chroma_documents, mock_filesystem):
    return _make_index_service(chroma_documents=mock_chroma_documents, filesystem=mock_filesystem)


@pytest.fixture
def tool(index_service, mock_console_service):
    return FindZkDocumentsRelatedTo(index_service, mock_console_service)


class DescribeFormatDocumentResults:
    """Tests for the format_model_results function with ZkQueryDocumentResult objects."""

    def should_return_empty_json_array_for_no_results(self):
        result = format_model_results([])

        parsed = json.loads(result)
        assert parsed == []

    def should_serialize_single_result_to_json(self):
        results = [
            ZkQueryDocumentResult(
                document=ZkDocument(relative_path="notes/doc.md", metadata={}, content="Content"),
                distance=0.5,
            )
        ]

        result = format_model_results(results)

        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["document"]["relative_path"] == "notes/doc.md"
        assert parsed[0]["distance"] == 0.5

    def should_serialize_multiple_results_preserving_order(self):
        results = [
            ZkQueryDocumentResult(
                document=ZkDocument(relative_path="doc1", metadata={}, content="First"),
                distance=0.8,
            ),
            ZkQueryDocumentResult(
                document=ZkDocument(relative_path="doc2", metadata={}, content="Second"),
                distance=0.7,
            ),
        ]

        result = format_model_results(results)

        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["document"]["relative_path"] == "doc1"
        assert parsed[1]["document"]["relative_path"] == "doc2"


class DescribeFindZkDocumentsRelatedTo:
    """Tests for the FindZkDocumentsRelatedTo tool."""

    def should_return_json_list_of_document_results_with_distances(self, tool, mock_chroma_documents, mock_filesystem):
        mock_chroma_documents.query.return_value = {
            "ids": [["doc1", "doc2"]],
            "documents": [["First Document", "Second Document"]],
            "metadatas": [[{"id": "doc1", "title": "First"}, {"id": "doc2", "title": "Second"}]],
            "distances": [[0.8, 0.7]],
        }
        mock_filesystem.read_markdown.side_effect = [
            ({"title": "First"}, "First Document"),
            ({"title": "Second"}, "Second Document"),
        ]

        result = tool.run("test query")

        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["distance"] == 0.8
        assert parsed[0]["document"]["relative_path"] == "doc1"
        assert parsed[1]["distance"] == 0.7
        assert parsed[1]["document"]["relative_path"] == "doc2"
