import json
from unittest.mock import Mock

import pytest

from zk_chat.models import ZkDocument, ZkQueryDocumentResult
from zk_chat.services.index_service import IndexService
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo


@pytest.fixture
def mock_index_service():
    return Mock(spec=IndexService)


@pytest.fixture
def tool(mock_index_service):
    return FindZkDocumentsRelatedTo(mock_index_service)


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
