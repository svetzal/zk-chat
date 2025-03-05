import json
from typing import List

import pytest
from mojentic.llm.tools.llm_tool import LLMTool
from pytest_mock import MockerFixture

from zk_chat.models import ZkDocumentExcerpt, ZkQueryResult
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
        ZkQueryResult(
            excerpt=ZkDocumentExcerpt(
                document_id="doc1",
                document_title="First Document",
                text="chunk1"
            ),
            distance=0.8
        ),
        ZkQueryResult(
            excerpt=ZkDocumentExcerpt(
                document_id="doc2",
                document_title="Second Document",
                text="chunk2"
            ),
            distance=0.7
        )
    ]
    mock_zk.query_excerpts.return_value = query_results

    result = tool.run("test query")
    expected = [
        {"id": "doc1", "title": "First Document"},
        {"id": "doc2", "title": "Second Document"}
    ]

    assert json.loads(result) == expected
