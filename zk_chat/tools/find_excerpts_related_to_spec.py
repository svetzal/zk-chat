import json

import pytest

from zk_chat.tools.conftest import _make_index_service
from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo


@pytest.fixture
def index_service(mock_chroma_excerpts):
    return _make_index_service(chroma_excerpts=mock_chroma_excerpts)


@pytest.fixture
def find_excerpts_tool(index_service, mock_console_gateway):
    return FindExcerptsRelatedTo(index_service, mock_console_gateway)


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
