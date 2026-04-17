import json
from unittest.mock import Mock

import pytest

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.models import ZkDocumentExcerpt, ZkQueryExcerptResult
from zk_chat.tools.conftest import _make_index_service
from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo
from zk_chat.tools.tool_helpers import format_model_results


@pytest.fixture
def mock_chroma_excerpts():
    return Mock(spec=ChromaGateway)


@pytest.fixture
def index_service(mock_chroma_excerpts):
    return _make_index_service(chroma_excerpts=mock_chroma_excerpts)


@pytest.fixture
def find_excerpts_tool(index_service, mock_console_service):
    return FindExcerptsRelatedTo(index_service, mock_console_service)


class DescribeFormatExcerptResults:
    """Tests for the format_model_results function with ZkQueryExcerptResult objects."""

    def should_return_empty_json_array_for_no_results(self):
        result = format_model_results([])

        parsed = json.loads(result)
        assert parsed == []

    def should_serialize_single_result_to_json(self):
        results = [
            ZkQueryExcerptResult(
                excerpt=ZkDocumentExcerpt(document_id="doc1", document_title="Test Doc", text="Sample text"),
                distance=0.1,
            )
        ]

        result = format_model_results(results)

        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["excerpt"]["document_id"] == "doc1"
        assert parsed[0]["distance"] == 0.1

    def should_serialize_multiple_results_preserving_order(self):
        results = [
            ZkQueryExcerptResult(
                excerpt=ZkDocumentExcerpt(document_id="doc1", document_title="First", text="text1"),
                distance=0.1,
            ),
            ZkQueryExcerptResult(
                excerpt=ZkDocumentExcerpt(document_id="doc2", document_title="Second", text="text2"),
                distance=0.2,
            ),
        ]

        result = format_model_results(results)

        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["excerpt"]["document_id"] == "doc1"
        assert parsed[1]["excerpt"]["document_id"] == "doc2"


class DescribeFindExcerptsRelatedTo:
    """Tests for the FindExcerptsRelatedTo tool."""

    def should_return_json_list_of_excerpt_results(self, find_excerpts_tool, mock_chroma_excerpts):
        mock_chroma_excerpts.query.return_value = {
            "ids": [["excerpt1", "excerpt2"]],
            "documents": [["Sample text 1", "Sample text 2"]],
            "metadatas": [[{"id": "doc1", "title": "Test Doc 1"}, {"id": "doc2", "title": "Test Doc 2"}]],
            "distances": [[0.1, 0.2]],
        }

        result = find_excerpts_tool.run("test query")

        mock_chroma_excerpts.query.assert_called_once()
        parsed_result = json.loads(result)
        assert len(parsed_result) == 2
        assert parsed_result[0]["excerpt"]["document_id"] == "doc1"
        assert parsed_result[0]["excerpt"]["document_title"] == "Test Doc 1"
        assert parsed_result[1]["excerpt"]["document_id"] == "doc2"
