import pytest
from mojentic.llm.gateways.models import MessageRole

from rag.chat_session import ChatSession


@pytest.fixture
def llm(mocker):
    llm = mocker.MagicMock()
    llm.generate.return_value = "Response message"
    return llm


@pytest.fixture
def tokenizer(mocker):
    tokenizer = mocker.MagicMock()
    tokenizer.encode.return_value = [1]  # Each message in the chat session will count as length 1
    return tokenizer


@pytest.fixture
def chat_session(llm, tokenizer):
    return ChatSession(llm=llm, system_prompt="You are a helpful assistant.", tokenizer_gateway=tokenizer,
                       max_context=3, temperature=1.0)


def test_fresh_session(chat_session):
    assert len(chat_session.messages) == 1


def test_query_responds_with_text(chat_session):
    response = chat_session.send("Query message")

    assert response == "Response message"


def test_session_length_grows_correctly(chat_session):
    _ = chat_session.send("Query message")

    assert len(chat_session.messages) == 3


def test_session_length_does_not_exceed_capacity(chat_session):
    _ = chat_session.send("Query message 1")
    _ = chat_session.send("Query message 2")

    assert len(chat_session.messages) == 3

def test_session_keeps_only_newest_messages(chat_session):
    _ = chat_session.send("Query message 1")
    _ = chat_session.send("Query message 2")

    assert chat_session.messages[0].content == "You are a helpful assistant."
    assert chat_session.messages[1].content == "Query message 2"
    assert chat_session.messages[2].content == "Response message"

def test_session_uses_appropriate_message_roles(chat_session):
    _ = chat_session.send("Query message")

    assert chat_session.messages[0].role == MessageRole.System
    assert chat_session.messages[1].role == MessageRole.User
    assert chat_session.messages[2].role == MessageRole.Assistant