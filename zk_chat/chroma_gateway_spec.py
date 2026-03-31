from unittest.mock import MagicMock, Mock, patch

import pytest
from chromadb.api.models.Collection import Collection

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import ModelGateway


@pytest.fixture
def mock_chroma_client():
    return MagicMock()


@pytest.fixture
def mock_collection():
    return Mock(spec=Collection)


@pytest.fixture
def gateway(mock_chroma_client):
    with patch("zk_chat.chroma_gateway.chromadb.PersistentClient", return_value=mock_chroma_client):
        return ChromaGateway(gateway=ModelGateway.OLLAMA, db_dir="/fake/db")


class DescribeChromaGateway:
    def should_initialize_persistent_client_at_gateway_subdirectory(self, mock_chroma_client):
        with patch(
            "zk_chat.chroma_gateway.chromadb.PersistentClient", return_value=mock_chroma_client
        ) as mock_persistent_client:
            ChromaGateway(gateway=ModelGateway.OLLAMA, db_dir="/fake/db")

            mock_persistent_client.assert_called_once()
            call_kwargs = mock_persistent_client.call_args
            assert call_kwargs.kwargs["path"] == "/fake/db/ollama"

    def should_initialize_with_empty_collections_cache(self, gateway):
        assert gateway._collections == {}

    class DescribeGetCollection:
        def should_create_collection_on_first_access(self, gateway, mock_chroma_client, mock_collection):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection

            result = gateway.get_collection(ZkCollectionName.EXCERPTS)

            mock_chroma_client.get_or_create_collection.assert_called_once_with(
                name=ZkCollectionName.EXCERPTS.value,
                metadata={"hsnw:space": "cosine"},
            )
            assert result is mock_collection

        def should_cache_collection_after_first_access(self, gateway, mock_chroma_client, mock_collection):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection

            gateway.get_collection(ZkCollectionName.EXCERPTS)
            gateway.get_collection(ZkCollectionName.EXCERPTS)

            mock_chroma_client.get_or_create_collection.assert_called_once()

        def should_cache_collections_independently_per_name(self, gateway, mock_chroma_client):
            mock_excerpts = Mock(spec=Collection)
            mock_documents = Mock(spec=Collection)
            mock_chroma_client.get_or_create_collection.side_effect = [mock_excerpts, mock_documents]

            result_excerpts = gateway.get_collection(ZkCollectionName.EXCERPTS)
            result_documents = gateway.get_collection(ZkCollectionName.DOCUMENTS)

            assert result_excerpts is mock_excerpts
            assert result_documents is mock_documents
            assert mock_chroma_client.get_or_create_collection.call_count == 2

    class DescribeAddItems:
        def should_upsert_items_into_collection(self, gateway, mock_chroma_client, mock_collection):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection
            test_ids = ["id1", "id2"]
            test_documents = ["doc1", "doc2"]
            test_metadatas = [{"key": "val1"}, {"key": "val2"}]
            test_embeddings = [[0.1, 0.2], [0.3, 0.4]]

            gateway.add_items(
                ids=test_ids,
                documents=test_documents,
                metadatas=test_metadatas,
                embeddings=test_embeddings,
                collection_name=ZkCollectionName.EXCERPTS,
            )

            mock_collection.upsert.assert_called_once_with(
                ids=test_ids,
                documents=test_documents,
                metadatas=test_metadatas,
                embeddings=test_embeddings,
            )

    class DescribeResetIndexes:
        def should_reset_specific_collection_and_recreate_it(self, gateway, mock_chroma_client, mock_collection):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection

            gateway.reset_indexes(ZkCollectionName.EXCERPTS)

            mock_chroma_client.delete_collection.assert_called_once_with(ZkCollectionName.EXCERPTS.value)
            mock_chroma_client.get_or_create_collection.assert_called_once_with(
                name=ZkCollectionName.EXCERPTS.value,
                metadata={"hsnw:space": "cosine"},
            )

        def should_ignore_value_error_when_collection_does_not_exist(
            self, gateway, mock_chroma_client, mock_collection
        ):
            mock_chroma_client.delete_collection.side_effect = ValueError("not found")
            mock_chroma_client.get_or_create_collection.return_value = mock_collection

            gateway.reset_indexes(ZkCollectionName.EXCERPTS)

            mock_chroma_client.get_or_create_collection.assert_called_once()

        def should_remove_collection_from_cache_before_recreating(
            self, gateway, mock_chroma_client, mock_collection
        ):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection
            gateway._collections[ZkCollectionName.EXCERPTS] = mock_collection

            gateway.reset_indexes(ZkCollectionName.EXCERPTS)

            assert ZkCollectionName.EXCERPTS in gateway._collections

        def should_reset_all_collections_when_no_name_given(self, gateway, mock_chroma_client):
            gateway._collections[ZkCollectionName.EXCERPTS] = Mock(spec=Collection)

            gateway.reset_indexes()

            mock_chroma_client.reset.assert_called_once()
            assert gateway._collections == {}

    class DescribeQuery:
        def should_query_collection_with_embeddings_and_result_count(
            self, gateway, mock_chroma_client, mock_collection
        ):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection
            test_embeddings = [[0.1, 0.2, 0.3]]
            expected_results = {"ids": [["id1"]], "documents": [["doc1"]]}
            mock_collection.query.return_value = expected_results

            result = gateway.query(
                query_embeddings=test_embeddings,
                n_results=5,
                collection_name=ZkCollectionName.EXCERPTS,
            )

            mock_collection.query.assert_called_once_with(
                query_embeddings=test_embeddings,
                n_results=5,
            )
            assert result == expected_results
