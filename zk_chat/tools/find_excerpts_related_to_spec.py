import json
from unittest.mock import Mock

import pytest

from zk_chat.models import ZkDocumentExcerpt, ZkQueryExcerptResult
from zk_chat.services.index_service import IndexService
from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo


@pytest.fixture
def mock_index_service():
    return Mock(spec=IndexService)


@pytest.fixture
def find_excerpts_tool(mock_index_service):
    return FindExcerptsRelatedTo(mock_index_service)


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
