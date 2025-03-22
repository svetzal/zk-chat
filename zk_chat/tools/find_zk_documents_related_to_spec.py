import json
from typing import List

import pytest
from mojentic.llm.tools.llm_tool import LLMTool
from pytest_mock import MockerFixture

from zk_chat.models import ZkDocumentExcerpt, ZkQueryExcerptResult, ZkQueryDocumentResult, ZkDocument
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo
from zk_chat.zettelkasten import Zettelkasten


@pytest.fixture
def mock_zk(mocker: MockerFixture) -> Zettelkasten:
    return mocker.Mock(spec=Zettelkasten)


@pytest.fixture
def tool(mock_zk: Zettelkasten) -> LLMTool:
    return FindZkDocumentsRelatedTo(mock_zk)


def test_run_returns_document_ids_and_titles(
    tool: FindZkDocumentsRelatedTo,
    mock_zk: Zettelkasten,
):
    query_results = [
        ZkQueryDocumentResult(
            document=ZkDocument(
                relative_path="doc1",
                content="First Document",
                metadata={},
            ),
            distance=0.8
        ),
        ZkQueryDocumentResult(
            document=ZkDocument(
                relative_path="doc2",
                content="Second Document",
                metadata={},
            ),
            distance=0.7
        )
    ]
    mock_zk.query_documents.return_value = query_results

    result = tool.run("test query")
    expected = [
        {"distance": 0.8, "document": {"relative_path": "doc1", "content": "First Document", "metadata": {}}},
        {"distance": 0.7, "document": {"relative_path": "doc2", "content": "Second Document", "metadata":{}}},
    ]

    assert json.loads(result) == expected
