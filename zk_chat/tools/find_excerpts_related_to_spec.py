import json

import pytest
from pytest_mock import MockerFixture

from zk_chat.models import ZkQueryResult, ZkDocumentExcerpt
from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo


@pytest.fixture
def mock_zk(mocker: MockerFixture):
    return mocker.Mock()


@pytest.fixture
def find_excerpts_tool(mock_zk):
    return FindExcerptsRelatedTo(mock_zk)


def test_find_excerpts_related_to(find_excerpts_tool, mock_zk):
    query = "test query"
    mock_results = [
        ZkQueryResult(
            excerpt=ZkDocumentExcerpt(
                document_id="doc1",
                document_title="Test Doc 1",
                text="Sample text 1"
            ),
            distance=0.1
        ),
        ZkQueryResult(
            excerpt=ZkDocumentExcerpt(
                document_id="doc2",
                document_title="Test Doc 2",
                text="Sample text 2"
            ),
            distance=0.2
        )
    ]
    mock_zk.query_excerpts.return_value = mock_results

    result = find_excerpts_tool.run(query)

    mock_zk.query_excerpts.assert_called_once_with(query)
    assert result == json.dumps([result.model_dump() for result in mock_results])
