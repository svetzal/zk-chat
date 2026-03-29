import json
from unittest.mock import Mock

import pytest

from zk_chat.console_service import RichConsoleService
from zk_chat.models import ZkDocument, ZkQueryDocumentResult
from zk_chat.services.index_service import IndexService
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo
from zk_chat.tools.tool_helpers import format_model_results


@pytest.fixture
def mock_index_service():
    return Mock(spec=IndexService)


@pytest.fixture
def mock_console_service():
    return Mock(spec=RichConsoleService)


@pytest.fixture
def tool(mock_index_service, mock_console_service):
    return FindZkDocumentsRelatedTo(mock_index_service, mock_console_service)


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

    def should_return_json_list_of_document_results_with_distances(self, tool, mock_index_service):
        mock_results = [
            ZkQueryDocumentResult(
                document=ZkDocument(relative_path="doc1", metadata={}, content="First Document"), distance=0.8
            ),
            ZkQueryDocumentResult(
                document=ZkDocument(relative_path="doc2", metadata={}, content="Second Document"), distance=0.7
            ),
        ]
        mock_index_service.query_documents.return_value = mock_results

        result = tool.run("test query")

        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["distance"] == 0.8
        assert parsed[0]["document"]["relative_path"] == "doc1"
        assert parsed[1]["distance"] == 0.7
        assert parsed[1]["document"]["relative_path"] == "doc2"
