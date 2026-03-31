from unittest.mock import MagicMock, Mock

import pytest
from mojentic.llm.gateways.models import LLMMessage, MessageRole

from zk_chat.rag.query import rag_query


@pytest.fixture
def mock_chat_session():
    return MagicMock()


@pytest.fixture
def mock_zk():
    return MagicMock()


def make_result(title: str, text: str) -> Mock:
    result = Mock()
    result.excerpt.document_title = title
    result.excerpt.text = text
    return result


class DescribeRagQuery:
    def should_insert_one_message_per_result_and_send_query(self, mock_chat_session, mock_zk):
        test_query = "What is zk-chat?"
        result_a = make_result("Note A", "Content from note A")
        result_b = make_result("Note B", "Content from note B")
        mock_zk.query_excerpts.return_value = [result_a, result_b]
        expected_response = "The answer"
        mock_chat_session.send.return_value = expected_response

        response = rag_query(mock_chat_session, mock_zk, test_query)

        mock_zk.query_excerpts.assert_called_once_with(test_query, n_results=10, max_distance=1.0)
        assert mock_chat_session.insert_message.call_count == 2
        assert response == expected_response

    def should_insert_messages_with_correct_role_and_content(self, mock_chat_session, mock_zk):
        test_query = "test query"
        result_a = make_result("My Note", "Some text here")
        mock_zk.query_excerpts.return_value = [result_a]

        rag_query(mock_chat_session, mock_zk, test_query)

        inserted_message = mock_chat_session.insert_message.call_args[0][0]
        assert isinstance(inserted_message, LLMMessage)
        assert inserted_message.role == MessageRole.Assistant
        assert "My Note" in inserted_message.content
        assert "Some text here" in inserted_message.content

    def should_send_query_to_chat_session_after_inserting_messages(self, mock_chat_session, mock_zk):
        test_query = "my question"
        mock_zk.query_excerpts.return_value = [make_result("Note", "text")]

        rag_query(mock_chat_session, mock_zk, test_query)

        mock_chat_session.send.assert_called_once_with(test_query)

    def should_return_chat_session_send_result(self, mock_chat_session, mock_zk):
        mock_zk.query_excerpts.return_value = []
        mock_chat_session.send.return_value = "final answer"

        result = rag_query(mock_chat_session, mock_zk, "query")

        assert result == "final answer"

    def should_insert_no_messages_when_no_results(self, mock_chat_session, mock_zk):
        mock_zk.query_excerpts.return_value = []

        rag_query(mock_chat_session, mock_zk, "query")

        mock_chat_session.insert_message.assert_not_called()

    def should_still_send_query_when_no_results(self, mock_chat_session, mock_zk):
        test_query = "no results query"
        mock_zk.query_excerpts.return_value = []

        rag_query(mock_chat_session, mock_zk, test_query)

        mock_chat_session.send.assert_called_once_with(test_query)
