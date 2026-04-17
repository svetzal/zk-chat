from unittest.mock import ANY

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.conftest import STUB_EMBEDDING
from zk_chat.memory.smart_memory import SmartMemory


class DescribeSmartMemory:
    """
    Describes the behavior of SmartMemory component which provides an interface
    for storing and retrieving information using ChromaDB vector database
    """

    def should_be_instantiated_with_chroma_gateway(self, mock_chroma_gateway, mock_ollama_gateway):
        memory = SmartMemory(mock_chroma_gateway, mock_ollama_gateway)

        assert isinstance(memory, SmartMemory)
        assert memory.chroma == mock_chroma_gateway
        assert memory.gateway == mock_ollama_gateway

    def should_store_information_in_chroma_db(self, mock_chroma_gateway, mock_ollama_gateway):
        memory = SmartMemory(mock_chroma_gateway, mock_ollama_gateway)

        memory.store("some information")

        mock_ollama_gateway.calculate_embeddings.assert_called_once_with("some information")
        mock_chroma_gateway.add_items.assert_called_once_with(
            ids=[ANY],
            documents=["some information"],
            metadatas=None,
            embeddings=[STUB_EMBEDDING],
            collection_name=ZkCollectionName.SMART_MEMORY,
        )

    def should_retrieve_information_from_chroma_db_with_default_results(self, mock_chroma_gateway, mock_ollama_gateway):
        memory = SmartMemory(mock_chroma_gateway, mock_ollama_gateway)

        _ = memory.retrieve("some information")

        mock_ollama_gateway.calculate_embeddings.assert_called_once_with("some information")
        mock_chroma_gateway.query.assert_called_once_with(
            query_embeddings=ANY, n_results=5, collection_name=ZkCollectionName.SMART_MEMORY
        )

    def should_retrieve_information_from_chroma_db_with_custom_results(self, mock_chroma_gateway, mock_ollama_gateway):
        memory = SmartMemory(mock_chroma_gateway, mock_ollama_gateway)

        _ = memory.retrieve("some information", n_results=10)

        mock_ollama_gateway.calculate_embeddings.assert_called_once_with("some information")
        mock_chroma_gateway.query.assert_called_once_with(
            query_embeddings=ANY, n_results=10, collection_name=ZkCollectionName.SMART_MEMORY
        )

    def should_reset_smart_memory(self, mock_chroma_gateway, mock_ollama_gateway):
        """Tests that the reset method properly clears the smart memory"""
        memory = SmartMemory(mock_chroma_gateway, mock_ollama_gateway)

        memory.reset()

        mock_chroma_gateway.reset_indexes.assert_called_once_with(collection_name=ZkCollectionName.SMART_MEMORY)
