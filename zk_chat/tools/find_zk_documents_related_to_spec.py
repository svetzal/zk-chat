import json

import pytest

from zk_chat.tools.conftest import _make_index_service
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo


@pytest.fixture
def index_service(mock_chroma_documents, mock_filesystem):
    return _make_index_service(chroma_documents=mock_chroma_documents, filesystem=mock_filesystem)


@pytest.fixture
def tool(index_service, mock_console_gateway):
    return FindZkDocumentsRelatedTo(index_service, mock_console_gateway)


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
