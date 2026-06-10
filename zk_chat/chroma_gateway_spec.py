# ChromaGateway wraps chromadb — Collection mocks are the library boundary this gateway abstracts.

from unittest.mock import MagicMock, Mock, patch

import pytest
import structlog.testing
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
def chroma_gateway(mock_chroma_client):
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

    def should_initialize_with_empty_collections_cache(self, chroma_gateway):
        assert chroma_gateway._collections == {}

    class DescribeGetCollection:
        def should_create_collection_on_first_access(self, chroma_gateway, mock_chroma_client, mock_collection):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection

            result = chroma_gateway.get_collection(ZkCollectionName.EXCERPTS)

            mock_chroma_client.get_or_create_collection.assert_called_once_with(
                name=ZkCollectionName.EXCERPTS.value,
                metadata={"hsnw:space": "cosine"},
            )
            assert result is mock_collection

        def should_cache_collection_after_first_access(self, chroma_gateway, mock_chroma_client, mock_collection):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection

            chroma_gateway.get_collection(ZkCollectionName.EXCERPTS)
            chroma_gateway.get_collection(ZkCollectionName.EXCERPTS)

            mock_chroma_client.get_or_create_collection.assert_called_once()

        def should_cache_collections_independently_per_name(self, chroma_gateway, mock_chroma_client):
            mock_excerpts = Mock(spec=Collection)
            mock_documents = Mock(spec=Collection)
            mock_chroma_client.get_or_create_collection.side_effect = [mock_excerpts, mock_documents]

            result_excerpts = chroma_gateway.get_collection(ZkCollectionName.EXCERPTS)
            result_documents = chroma_gateway.get_collection(ZkCollectionName.DOCUMENTS)

            assert result_excerpts is mock_excerpts
            assert result_documents is mock_documents
            assert mock_chroma_client.get_or_create_collection.call_count == 2

    class DescribeAddItems:
        def should_upsert_items_into_collection(self, chroma_gateway, mock_chroma_client, mock_collection):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection
            test_ids = ["id1", "id2"]
            test_documents = ["doc1", "doc2"]
            test_metadatas = [{"key": "val1"}, {"key": "val2"}]
            test_embeddings = [[0.1, 0.2], [0.3, 0.4]]

            chroma_gateway.add_items(
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

    class DescribeDeleteItems:
        def should_delete_items_by_ids(self, chroma_gateway, mock_chroma_client, mock_collection):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection
            test_ids = ["id1", "id2"]

            chroma_gateway.delete_items(
                collection_name=ZkCollectionName.EXCERPTS,
                ids=test_ids,
            )

            mock_collection.delete.assert_called_once_with(ids=test_ids, where=None)

        def should_delete_items_by_where_filter(self, chroma_gateway, mock_chroma_client, mock_collection):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection
            test_where = {"document_path": "doc.md"}

            chroma_gateway.delete_items(
                collection_name=ZkCollectionName.EXCERPTS,
                where=test_where,
            )

            mock_collection.delete.assert_called_once_with(ids=None, where=test_where)

    class DescribeResetIndexes:
        def should_reset_specific_collection_and_recreate_it(self, chroma_gateway, mock_chroma_client, mock_collection):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection

            chroma_gateway.reset_indexes(ZkCollectionName.EXCERPTS)

            mock_chroma_client.delete_collection.assert_called_once_with(ZkCollectionName.EXCERPTS.value)
            mock_chroma_client.get_or_create_collection.assert_called_once_with(
                name=ZkCollectionName.EXCERPTS.value,
                metadata={"hsnw:space": "cosine"},
            )

        def should_ignore_value_error_when_collection_does_not_exist(
            self, chroma_gateway, mock_chroma_client, mock_collection
        ):
            mock_chroma_client.delete_collection.side_effect = ValueError("not found")
            mock_chroma_client.get_or_create_collection.return_value = mock_collection

            chroma_gateway.reset_indexes(ZkCollectionName.EXCERPTS)

            mock_chroma_client.get_or_create_collection.assert_called_once()

        def should_remove_collection_from_cache_before_recreating(
            self, chroma_gateway, mock_chroma_client, mock_collection
        ):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection
            chroma_gateway._collections[ZkCollectionName.EXCERPTS] = mock_collection

            chroma_gateway.reset_indexes(ZkCollectionName.EXCERPTS)

            assert ZkCollectionName.EXCERPTS in chroma_gateway._collections

        def should_reset_all_collections_when_no_name_given(self, chroma_gateway, mock_chroma_client):
            chroma_gateway._collections[ZkCollectionName.EXCERPTS] = Mock(spec=Collection)

            chroma_gateway.reset_indexes()

            mock_chroma_client.reset.assert_called_once()
            assert chroma_gateway._collections == {}

    class DescribeQuery:
        def should_query_collection_with_embeddings_and_result_count(
            self, chroma_gateway, mock_chroma_client, mock_collection
        ):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection
            test_embeddings = [[0.1, 0.2, 0.3]]
            expected_results = {"ids": [["id1"]], "documents": [["doc1"]]}
            mock_collection.query.return_value = expected_results

            result = chroma_gateway.query(
                query_embeddings=test_embeddings,
                n_results=5,
                collection_name=ZkCollectionName.EXCERPTS,
            )

            mock_collection.query.assert_called_once_with(
                query_embeddings=test_embeddings,
                n_results=5,
            )
            assert result == expected_results

    class DescribeLogging:
        def should_log_debug_when_adding_items(self, chroma_gateway, mock_chroma_client, mock_collection):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection

            with structlog.testing.capture_logs() as cap_logs:
                chroma_gateway.add_items(
                    ids=["id1", "id2"],
                    documents=["doc1", "doc2"],
                    metadatas=[{}, {}],
                    embeddings=[[0.1], [0.2]],
                    collection_name=ZkCollectionName.EXCERPTS,
                )

            debug_logs = [e for e in cap_logs if e.get("log_level") == "debug"]
            assert any("Adding items" in e["event"] for e in debug_logs)

        def should_log_debug_when_collection_missing_during_reset(
            self, chroma_gateway, mock_chroma_client, mock_collection
        ):
            mock_chroma_client.delete_collection.side_effect = ValueError("not found")
            mock_chroma_client.get_or_create_collection.return_value = mock_collection

            with structlog.testing.capture_logs() as cap_logs:
                chroma_gateway.reset_indexes(ZkCollectionName.EXCERPTS)

            debug_logs = [e for e in cap_logs if e.get("log_level") == "debug"]
            assert any("did not exist" in e["event"] for e in debug_logs)

        def should_log_debug_when_querying(self, chroma_gateway, mock_chroma_client, mock_collection):
            mock_chroma_client.get_or_create_collection.return_value = mock_collection
            mock_collection.query.return_value = {"ids": [["id1"]], "documents": [["doc1"]]}

            with structlog.testing.capture_logs() as cap_logs:
                chroma_gateway.query(
                    query_embeddings=[[0.1, 0.2]],
                    n_results=3,
                    collection_name=ZkCollectionName.EXCERPTS,
                )

            debug_logs = [e for e in cap_logs if e.get("log_level") == "debug"]
            assert any("Querying collection" in e["event"] for e in debug_logs)
