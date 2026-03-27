import json
from unittest.mock import Mock

import pytest

from zk_chat.console_service import RichConsoleService
from zk_chat.models import ZkDocumentExcerpt, ZkQueryExcerptResult
from zk_chat.services.index_service import IndexService
from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo, format_excerpt_results


@pytest.fixture
def mock_index_service():
    return Mock(spec=IndexService)


@pytest.fixture
def mock_console_service():
    return Mock(spec=RichConsoleService)


@pytest.fixture
def find_excerpts_tool(mock_index_service, mock_console_service):
    return FindExcerptsRelatedTo(mock_index_service, mock_console_service)


class DescribeFormatExcerptResults:
    """Tests for the format_excerpt_results pure function."""

    def should_return_empty_json_array_for_no_results(self):
        result = format_excerpt_results([])

        parsed = json.loads(result)
        assert parsed == []

    def should_serialize_single_result_to_json(self):
        results = [
            ZkQueryExcerptResult(
                excerpt=ZkDocumentExcerpt(document_id="doc1", document_title="Test Doc", text="Sample text"),
                distance=0.1,
            )
        ]

        result = format_excerpt_results(results)

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

        result = format_excerpt_results(results)

        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["excerpt"]["document_id"] == "doc1"
        assert parsed[1]["excerpt"]["document_id"] == "doc2"


class DescribeFindExcerptsRelatedTo:
    """Tests for the FindExcerptsRelatedTo tool."""

    def should_return_json_list_of_excerpt_results(self, find_excerpts_tool, mock_index_service):
        mock_results = [
            ZkQueryExcerptResult(
                excerpt=ZkDocumentExcerpt(document_id="doc1", document_title="Test Doc 1", text="Sample text 1"),
                distance=0.1,
            ),
            ZkQueryExcerptResult(
                excerpt=ZkDocumentExcerpt(document_id="doc2", document_title="Test Doc 2", text="Sample text 2"),
                distance=0.2,
            ),
        ]
        mock_index_service.query_excerpts.return_value = mock_results

        result = find_excerpts_tool.run("test query")

        mock_index_service.query_excerpts.assert_called_once()
        parsed_result = json.loads(result)
        assert len(parsed_result) == 2
        assert parsed_result[0]["excerpt"]["document_id"] == "doc1"
        assert parsed_result[0]["excerpt"]["document_title"] == "Test Doc 1"
        assert parsed_result[1]["excerpt"]["document_id"] == "doc2"
