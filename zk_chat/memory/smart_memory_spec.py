from unittest.mock import Mock, ANY

import pytest
from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.memory.smart_memory import SmartMemory


@pytest.fixture
def mock_chroma_gateway():
    return Mock(spec=ChromaGateway)

@pytest.fixture
def mock_embeddings():
    return [0.1, 0.2, 0.3]

@pytest.fixture
def mock_embeddings_gateway(mock_embeddings):
    mock = Mock(spec=EmbeddingsGateway)
    mock.calculate.return_value = mock_embeddings
    return mock

class DescribeSmartMemory:
    """
    Describes the behavior of SmartMemory component which provides an interface
    for storing and retrieving information using ChromaDB vector database
    """

    def should_be_instantiated_with_chroma_gateway(self, mock_chroma_gateway, mock_embeddings_gateway):
        memory = SmartMemory(mock_chroma_gateway, mock_embeddings_gateway)

        assert isinstance(memory, SmartMemory)
        assert memory.chroma == mock_chroma_gateway
        assert memory.embeddings == mock_embeddings_gateway

    def should_store_information_in_chroma_db(self, mock_chroma_gateway, mock_embeddings_gateway, mock_embeddings):
        memory = SmartMemory(mock_chroma_gateway, mock_embeddings_gateway)

        memory.store("some information")

        mock_embeddings_gateway.calculate.assert_called_once_with("some information")
        mock_chroma_gateway.add_items.assert_called_once_with(
            ids=[ANY],
            documents=["some information"],
            metadatas=None,
            embeddings=[mock_embeddings]
        )

    def should_retrieve_information_from_chroma_db_with_default_results(self, mock_chroma_gateway, mock_embeddings_gateway):
        memory = SmartMemory(mock_chroma_gateway, mock_embeddings_gateway)

        _ = memory.retrieve("some information")

        mock_embeddings_gateway.calculate.assert_called_once_with("some information")
        mock_chroma_gateway.query.assert_called_once_with(
            query_embeddings=ANY,
            n_results=5
        )

    def should_retrieve_information_from_chroma_db_with_custom_results(self, mock_chroma_gateway, mock_embeddings_gateway):
        memory = SmartMemory(mock_chroma_gateway, mock_embeddings_gateway)

        _ = memory.retrieve("some information", n_results=10)

        mock_embeddings_gateway.calculate.assert_called_once_with("some information")
        mock_chroma_gateway.query.assert_called_once_with(
            query_embeddings=ANY,
            n_results=10
        )

    def should_reset_smart_memory(self, mock_chroma_gateway, mock_embeddings_gateway):
        """Tests that the reset method properly clears the smart memory"""
        memory = SmartMemory(mock_chroma_gateway, mock_embeddings_gateway)

        memory.reset()

        mock_chroma_gateway.reset_indexes.assert_called_once()
