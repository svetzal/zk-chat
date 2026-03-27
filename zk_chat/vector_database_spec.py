"""
Tests for VectorDatabase — the ChromaDB-backed vector store.
"""

from unittest.mock import Mock

import pytest
from mojentic.llm.gateways import OllamaGateway

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.models import VectorDocumentForStorage
from zk_chat.vector_database import VectorDatabase


@pytest.fixture
def mock_chroma_gateway():
    return Mock(spec=ChromaGateway)


@pytest.fixture
def mock_gateway():
    return Mock(spec=OllamaGateway)


@pytest.fixture
def vector_db(mock_chroma_gateway, mock_gateway):
    return VectorDatabase(mock_chroma_gateway, mock_gateway, ZkCollectionName.DOCUMENTS)


class DescribeVectorDatabase:
    """Tests for the VectorDatabase class."""

    class DescribeQuery:
        """Tests for the query method."""

        def should_build_query_results_from_chroma_response(self, vector_db, mock_chroma_gateway, mock_gateway):
            mock_gateway.calculate_embeddings.return_value = [0.1, 0.2, 0.3]
            mock_chroma_gateway.query.return_value = {
                "ids": [["id1", "id2"]],
                "documents": [["doc1 content", "doc2 content"]],
                "metadatas": [[{"title": "Doc1"}, {"title": "Doc2"}]],
                "distances": [[0.1, 0.5]],
            }

            result = vector_db.query("search text", n_results=2)

            assert len(result) == 2
            assert result[0].document.id == "id1"
            assert result[0].document.content == "doc1 content"
            assert result[0].distance == 0.1
            assert result[1].document.id == "id2"
            assert result[1].distance == 0.5

        def should_return_empty_list_when_no_results(self, vector_db, mock_chroma_gateway, mock_gateway):
            mock_gateway.calculate_embeddings.return_value = [0.1]
            mock_chroma_gateway.query.return_value = {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }

            result = vector_db.query("no match", n_results=5)

            assert result == []

        def should_pass_calculated_embeddings_to_chroma(self, vector_db, mock_chroma_gateway, mock_gateway):
            mock_gateway.calculate_embeddings.return_value = [0.5, 0.6]
            mock_chroma_gateway.query.return_value = {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }

            vector_db.query("test query", n_results=3)

            mock_chroma_gateway.query.assert_called_once_with(
                query_embeddings=[0.5, 0.6],
                n_results=3,
                collection_name=ZkCollectionName.DOCUMENTS,
            )

        def should_pass_correct_collection_name_to_chroma(self, mock_chroma_gateway, mock_gateway):
            excerpts_db = VectorDatabase(mock_chroma_gateway, mock_gateway, ZkCollectionName.EXCERPTS)
            mock_gateway.calculate_embeddings.return_value = [0.1]
            mock_chroma_gateway.query.return_value = {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }

            excerpts_db.query("test", n_results=1)

            mock_chroma_gateway.query.assert_called_once_with(
                query_embeddings=[0.1],
                n_results=1,
                collection_name=ZkCollectionName.EXCERPTS,
            )

    class DescribeAddDocuments:
        """Tests for the add_documents method."""

        def should_calculate_embeddings_for_each_document(self, vector_db, mock_chroma_gateway, mock_gateway):
            mock_gateway.calculate_embeddings.return_value = [0.1, 0.2]
            documents = [
                VectorDocumentForStorage(id="doc1", content="content1", metadata={}),
                VectorDocumentForStorage(id="doc2", content="content2", metadata={}),
            ]

            vector_db.add_documents(documents)

            assert mock_gateway.calculate_embeddings.call_count == 2

        def should_pass_documents_with_embeddings_to_chroma(self, vector_db, mock_chroma_gateway, mock_gateway):
            test_embedding = [0.1, 0.2, 0.3]
            mock_gateway.calculate_embeddings.return_value = test_embedding
            document = VectorDocumentForStorage(id="doc1", content="content1", metadata={"title": "Test"})

            vector_db.add_documents([document])

            mock_chroma_gateway.add_items.assert_called_once_with(
                ids=["doc1"],
                documents=["content1"],
                metadatas=[{"title": "Test"}],
                embeddings=[test_embedding],
                collection_name=ZkCollectionName.DOCUMENTS,
            )

    class DescribeReset:
        """Tests for the reset method."""

        def should_delegate_reset_to_chroma_gateway(self, vector_db, mock_chroma_gateway):
            vector_db.reset()

            mock_chroma_gateway.reset_indexes.assert_called_once_with(collection_name=ZkCollectionName.DOCUMENTS)
