"""
Tests for the IndexService which handles vector indexing and semantic search in a Zettelkasten.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.services.index_service import IndexService, IndexStats
from zk_chat.vector_database import VectorDatabase


@pytest.fixture
def mock_chroma_excerpts():
    return Mock(spec=ChromaGateway)


@pytest.fixture
def mock_chroma_documents():
    return Mock(spec=ChromaGateway)


@pytest.fixture
def excerpts_db(mock_chroma_excerpts, mock_ollama_gateway):
    return VectorDatabase(
        chroma_gateway=mock_chroma_excerpts,
        gateway=mock_ollama_gateway,
        collection_name=ZkCollectionName.EXCERPTS,
    )


@pytest.fixture
def documents_db(mock_chroma_documents, mock_ollama_gateway):
    return VectorDatabase(
        chroma_gateway=mock_chroma_documents,
        gateway=mock_ollama_gateway,
        collection_name=ZkCollectionName.DOCUMENTS,
    )


@pytest.fixture
def index_service(mock_tokenizer, excerpts_db, documents_db, mock_filesystem):
    return IndexService(
        tokenizer_gateway=mock_tokenizer,
        excerpts_db=excerpts_db,
        documents_db=documents_db,
        filesystem_gateway=mock_filesystem,
    )


class DescribeIndexService:
    """Tests for the IndexService component which handles vector indexing and search."""

    @pytest.fixture
    def mock_tokenizer(self):
        tokenizer = Mock(spec=TokenizerGateway)
        tokenizer.encode.return_value = [1, 2, 3, 4, 5] * 100  # 500 tokens
        tokenizer.decode.return_value = "decoded text"
        return tokenizer

    @pytest.fixture
    def sample_document_data(self):
        return ({"title": "Test Document", "tags": ["test"]}, "# Test Document\n\nThis is test content for indexing.")

    def should_be_instantiated_with_required_dependencies(
        self, mock_tokenizer, excerpts_db, documents_db, mock_filesystem
    ):
        service = IndexService(
            tokenizer_gateway=mock_tokenizer,
            excerpts_db=excerpts_db,
            documents_db=documents_db,
            filesystem_gateway=mock_filesystem,
        )

        assert isinstance(service, IndexService)
        assert service.tokenizer_gateway == mock_tokenizer
        assert service.excerpts_db == excerpts_db
        assert service.documents_db == documents_db
        assert service.filesystem_gateway == mock_filesystem

    def should_reindex_all_documents(
        self, index_service, mock_filesystem, mock_chroma_excerpts, mock_chroma_documents, sample_document_data
    ):
        mock_filesystem.iterate_markdown_files.return_value = ["doc1.md", "doc2.md"]
        mock_filesystem.read_markdown.return_value = sample_document_data

        index_service.reindex_all()

        mock_chroma_excerpts.reset_indexes.assert_called_once_with(collection_name=ZkCollectionName.EXCERPTS)
        mock_chroma_documents.reset_indexes.assert_called_once_with(collection_name=ZkCollectionName.DOCUMENTS)
        assert mock_filesystem.read_markdown.call_count == 2
        assert mock_chroma_documents.add_items.call_count == 2

    def should_call_progress_callback_during_reindex(self, index_service, mock_filesystem, sample_document_data):
        mock_filesystem.iterate_markdown_files.return_value = ["doc1.md", "doc2.md"]
        mock_filesystem.read_markdown.return_value = sample_document_data
        mock_callback = Mock()  # Intentionally unspec'd: bare callable, not a class instance

        index_service.reindex_all(progress_callback=mock_callback)

        assert mock_callback.call_count == 2
        mock_callback.assert_any_call("doc1.md", 1, 2)
        mock_callback.assert_any_call("doc2.md", 2, 2)

    def should_update_index_for_modified_documents(self, index_service, mock_filesystem, sample_document_data):
        since = datetime.now() - timedelta(hours=1)
        old_time = datetime.now() - timedelta(days=1)
        new_time = datetime.now()

        mock_filesystem.iterate_markdown_files.return_value = ["old.md", "new.md"]
        mock_filesystem.get_modified_time.side_effect = [old_time, new_time]
        mock_filesystem.read_markdown.return_value = sample_document_data

        index_service.update_index(since=since)

        assert mock_filesystem.read_markdown.call_count == 1
        mock_filesystem.read_markdown.assert_called_with("new.md")

    def should_index_single_document(self, index_service, mock_filesystem, mock_chroma_documents, sample_document_data):
        mock_filesystem.read_markdown.return_value = sample_document_data

        index_service.index_document("test.md")

        mock_filesystem.read_markdown.assert_called_once_with("test.md")
        mock_chroma_documents.add_items.assert_called_once()

    def should_skip_empty_documents_during_indexing(self, index_service, mock_filesystem, mock_chroma_documents):
        mock_filesystem.read_markdown.return_value = ({}, "")

        index_service.index_document("empty.md")

        mock_chroma_documents.add_items.assert_not_called()


class DescribeIndexServiceQueries:
    """Tests for query functionality in IndexService."""

    @pytest.fixture
    def mock_chroma_excerpts_with_results(self):
        chroma = Mock(spec=ChromaGateway)
        chroma.query.return_value = {
            "ids": [["excerpt1"]],
            "documents": [["This is an excerpt"]],
            "metadatas": [[{"id": "doc1.md", "title": "Test Document"}]],
            "distances": [[0.5]],
        }
        return chroma

    @pytest.fixture
    def mock_chroma_documents_with_results(self):
        chroma = Mock(spec=ChromaGateway)
        chroma.query.return_value = {
            "ids": [["doc1.md"]],
            "documents": [["Full document content"]],
            "metadatas": [[{"id": "doc1.md", "title": "Test Document"}]],
            "distances": [[0.3]],
        }
        return chroma

    @pytest.fixture
    def index_service_with_results(
        self,
        mock_tokenizer,
        mock_chroma_excerpts_with_results,
        mock_chroma_documents_with_results,
        mock_ollama_gateway,
        mock_filesystem,
    ):
        excerpts_db = VectorDatabase(
            mock_chroma_excerpts_with_results, mock_ollama_gateway, ZkCollectionName.EXCERPTS
        )
        documents_db = VectorDatabase(
            mock_chroma_documents_with_results, mock_ollama_gateway, ZkCollectionName.DOCUMENTS
        )
        return IndexService(
            tokenizer_gateway=mock_tokenizer,
            excerpts_db=excerpts_db,
            documents_db=documents_db,
            filesystem_gateway=mock_filesystem,
        )

    def should_query_excerpts_with_distance_filter(self, index_service_with_results, mock_chroma_excerpts_with_results):
        results = index_service_with_results.query_excerpts("test query", n_results=5, max_distance=1.0)

        mock_chroma_excerpts_with_results.query.assert_called_once()
        assert len(results) == 1
        assert results[0].excerpt.document_id == "doc1.md"
        assert results[0].distance == 0.5

    def should_filter_excerpts_by_max_distance(self, mock_tokenizer, mock_filesystem, mock_ollama_gateway):
        chroma = Mock(spec=ChromaGateway)
        chroma.query.return_value = {
            "ids": [["excerpt1"]],
            "documents": [["Far excerpt"]],
            "metadatas": [[{"id": "doc1.md", "title": "Test"}]],
            "distances": [[2.0]],
        }
        excerpts_db = VectorDatabase(chroma, mock_ollama_gateway, ZkCollectionName.EXCERPTS)
        documents_db = VectorDatabase(Mock(spec=ChromaGateway), mock_ollama_gateway, ZkCollectionName.DOCUMENTS)
        service = IndexService(mock_tokenizer, excerpts_db, documents_db, mock_filesystem)

        results = service.query_excerpts("test query", max_distance=1.0)

        assert len(results) == 0

    def should_query_documents_and_read_full_content(self, index_service_with_results, mock_filesystem):
        mock_filesystem.read_markdown.return_value = ({"title": "Test Document"}, "Full document content")

        results = index_service_with_results.query_documents("test query", n_results=3)

        assert len(results) == 1
        assert results[0].document.content == "Full document content"

    def should_skip_missing_documents_in_query_results(self, index_service_with_results, mock_filesystem):
        mock_filesystem.read_markdown.side_effect = FileNotFoundError("Not found")

        results = index_service_with_results.query_documents("test query")

        assert len(results) == 0

    def should_filter_documents_by_max_distance(self, mock_tokenizer, mock_filesystem, mock_ollama_gateway):
        chroma = Mock(spec=ChromaGateway)
        chroma.query.return_value = {
            "ids": [["doc1.md"]],
            "documents": [["Far document"]],
            "metadatas": [[{"id": "doc1.md", "title": "Test"}]],
            "distances": [[2.0]],
        }
        excerpts_db = VectorDatabase(Mock(spec=ChromaGateway), mock_ollama_gateway, ZkCollectionName.EXCERPTS)
        documents_db = VectorDatabase(chroma, mock_ollama_gateway, ZkCollectionName.DOCUMENTS)
        service = IndexService(mock_tokenizer, excerpts_db, documents_db, mock_filesystem)

        results = service.query_documents("test query", max_distance=1.0)

        assert len(results) == 0


class DescribeIndexServiceStats:
    """Tests for index statistics in IndexService."""

    def should_return_index_stats(self, index_service, mock_filesystem):
        mock_filesystem.iterate_markdown_files.return_value = ["doc1.md", "doc2.md", "doc3.md"]

        stats = index_service.get_index_stats()

        assert isinstance(stats, IndexStats)
        assert stats.total_documents == 3
        assert stats.last_indexed is None

    def should_update_last_indexed_after_reindex(self, index_service, mock_filesystem):
        mock_filesystem.iterate_markdown_files.return_value = []

        before = datetime.now()
        index_service.reindex_all()
        after = datetime.now()

        stats = index_service.get_index_stats()
        assert stats.last_indexed is not None
        assert before <= stats.last_indexed <= after


class DescribeIndexServiceDocumentSplitting:
    """Tests for document splitting functionality in IndexService."""

    def should_split_large_documents_into_excerpts(
        self, index_service, mock_tokenizer, mock_chroma_excerpts, mock_filesystem
    ):
        mock_tokenizer.encode.return_value = list(range(1000))
        mock_tokenizer.decode.return_value = "decoded excerpt text"
        mock_filesystem.read_markdown.return_value = (
            {"title": "Large Document"},
            "A" * 5000,  # Large content
        )

        index_service.index_document("large.md", excerpt_size=500, excerpt_overlap=100)

        # Should have called decode for each chunk
        assert mock_tokenizer.decode.call_count > 1
        # Should add excerpts to the index
        mock_chroma_excerpts.add_items.assert_called()

    def should_use_custom_excerpt_size_and_overlap(
        self, index_service, mock_tokenizer, mock_filesystem, mock_chroma_excerpts
    ):
        mock_tokenizer.encode.return_value = list(range(300))  # 300 tokens
        mock_tokenizer.decode.return_value = "decoded"
        mock_filesystem.read_markdown.return_value = ({"title": "Test"}, "Content")

        index_service.index_document("test.md", excerpt_size=100, excerpt_overlap=20)

        # With 300 tokens, 100 size, 20 overlap: should create multiple chunks
        assert mock_tokenizer.decode.call_count >= 3
