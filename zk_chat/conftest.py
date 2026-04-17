from unittest.mock import Mock

import pytest
from mojentic.llm.gateways import OllamaGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.console_service import ConsoleGateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway

STUB_EMBEDDING = [0.1, 0.2, 0.3]


@pytest.fixture
def mock_filesystem():
    return Mock(spec=MarkdownFilesystemGateway)


@pytest.fixture
def mock_console_service():
    return Mock(spec=ConsoleGateway)


@pytest.fixture
def mock_chroma_gateway():
    return Mock(spec=ChromaGateway)


@pytest.fixture
def mock_tokenizer():
    return Mock(spec=TokenizerGateway)


@pytest.fixture
def mock_ollama_gateway():
    gateway = Mock(spec=OllamaGateway)
    gateway.calculate_embeddings.return_value = STUB_EMBEDDING
    return gateway
