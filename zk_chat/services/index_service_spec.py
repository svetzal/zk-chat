"""
Tests for the IndexService which handles vector indexing and semantic search in a Zettelkasten.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.models import QueryResult, VectorDocumentForStorage
from zk_chat.services.index_service import IndexService, IndexStats
from zk_chat.vector_database import VectorDatabase


class DescribeIndexService:
    """Tests for the IndexService component which handles vector indexing and search."""

    @pytest.fixture
    def mock_tokenizer(self):
        tokenizer = Mock(spec=TokenizerGateway)
        tokenizer.encode.return_value = [1, 2, 3, 4, 5] * 100  # 500 tokens
        tokenizer.decode.return_value = "decoded text"
        return tokenizer

    @pytest.fixture
    def mock_excerpts_db(self):
        return Mock(spec=VectorDatabase)

    @pytest.fixture
    def mock_documents_db(self):
        return Mock(spec=VectorDatabase)

    @pytest.fixture
    def mock_filesystem(self):
        return Mock(spec=MarkdownFilesystemGateway)

    @pytest.fixture
    def index_service(self, mock_tokenizer, mock_excerpts_db, mock_documents_db, mock_filesystem):
        return IndexService(
            tokenizer_gateway=mock_tokenizer,
            excerpts_db=mock_excerpts_db,
            documents_db=mock_documents_db,
            filesystem_gateway=mock_filesystem,
        )

    @pytest.fixture
    def sample_document_data(self):
        return ({"title": "Test Document", "tags": ["test"]}, "# Test Document\n\nThis is test content for indexing.")

    def should_be_instantiated_with_required_dependencies(
        self, mock_tokenizer, mock_excerpts_db, mock_documents_db, mock_filesystem
    ):
        service = IndexService(
            tokenizer_gateway=mock_tokenizer,
            excerpts_db=mock_excerpts_db,
            documents_db=mock_documents_db,
            filesystem_gateway=mock_filesystem,
        )

        assert isinstance(service, IndexService)
        assert service.tokenizer_gateway == mock_tokenizer
        assert service.excerpts_db == mock_excerpts_db
        assert service.documents_db == mock_documents_db
        assert service.filesystem_gateway == mock_filesystem

    def should_reindex_all_documents(
        self, index_service, mock_filesystem, mock_excerpts_db, mock_documents_db, sample_document_data
    ):
        mock_filesystem.iterate_markdown_files.return_value = ["doc1.md", "doc2.md"]
        mock_filesystem.read_markdown.return_value = sample_document_data

        index_service.reindex_all()

        mock_excerpts_db.reset.assert_called_once()
        mock_documents_db.reset.assert_called_once()
        assert mock_filesystem.read_markdown.call_count == 2
        assert mock_documents_db.add_documents.call_count == 2

    def should_call_progress_callback_during_reindex(self, index_service, mock_filesystem, sample_document_data):
        mock_filesystem.iterate_markdown_files.return_value = ["doc1.md", "doc2.md"]
        mock_filesystem.read_markdown.return_value = sample_document_data
        mock_callback = Mock()

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

    def should_index_single_document(self, index_service, mock_filesystem, mock_documents_db, sample_document_data):
        mock_filesystem.read_markdown.return_value = sample_document_data

        index_service.index_document("test.md")

        mock_filesystem.read_markdown.assert_called_once_with("test.md")
        mock_documents_db.add_documents.assert_called_once()

    def should_skip_empty_documents_during_indexing(self, index_service, mock_filesystem, mock_documents_db):
        mock_filesystem.read_markdown.return_value = ({}, "")

        index_service.index_document("empty.md")

        mock_documents_db.add_documents.assert_not_called()


class DescribeIndexServiceQueries:
    """Tests for query functionality in IndexService."""

    @pytest.fixture
    def mock_tokenizer(self):
        return Mock(spec=TokenizerGateway)

    @pytest.fixture
    def mock_excerpts_db(self):
        return Mock(spec=VectorDatabase)

    @pytest.fixture
    def mock_documents_db(self):
        return Mock(spec=VectorDatabase)

    @pytest.fixture
    def mock_filesystem(self):
        return Mock(spec=MarkdownFilesystemGateway)

    @pytest.fixture
    def index_service(self, mock_tokenizer, mock_excerpts_db, mock_documents_db, mock_filesystem):
        return IndexService(
            tokenizer_gateway=mock_tokenizer,
            excerpts_db=mock_excerpts_db,
            documents_db=mock_documents_db,
            filesystem_gateway=mock_filesystem,
        )

    @pytest.fixture
    def sample_excerpt_result(self):
        return QueryResult(
            document=VectorDocumentForStorage(
                id="excerpt1", content="This is an excerpt", metadata={"id": "doc1.md", "title": "Test Document"}
            ),
            distance=0.5,
        )

    @pytest.fixture
    def sample_document_result(self):
        return QueryResult(
            document=VectorDocumentForStorage(
                id="doc1.md", content="Full document content", metadata={"id": "doc1.md", "title": "Test Document"}
            ),
            distance=0.3,
        )

    def should_query_excerpts_with_distance_filter(self, index_service, mock_excerpts_db, sample_excerpt_result):
        mock_excerpts_db.query.return_value = [sample_excerpt_result]

        results = index_service.query_excerpts("test query", n_results=5, max_distance=1.0)

        mock_excerpts_db.query.assert_called_once_with("test query", n_results=5)
        assert len(results) == 1
        assert results[0].excerpt.document_id == "doc1.md"
        assert results[0].distance == 0.5

    def should_filter_excerpts_by_max_distance(self, index_service, mock_excerpts_db):
        far_result = QueryResult(
            document=VectorDocumentForStorage(
                id="excerpt1", content="Far excerpt", metadata={"id": "doc1.md", "title": "Test"}
            ),
            distance=2.0,
        )
        mock_excerpts_db.query.return_value = [far_result]

        results = index_service.query_excerpts("test query", max_distance=1.0)

        assert len(results) == 0

    def should_query_documents_and_read_full_content(
        self, index_service, mock_documents_db, mock_filesystem, sample_document_result
    ):
        mock_documents_db.query.return_value = [sample_document_result]
        mock_filesystem.read_markdown.return_value = ({"title": "Test Document"}, "Full document content")

        results = index_service.query_documents("test query", n_results=3)

        mock_documents_db.query.assert_called_once_with("test query", n_results=3)
        assert len(results) == 1
        assert results[0].document.content == "Full document content"

    def should_skip_missing_documents_in_query_results(
        self, index_service, mock_documents_db, mock_filesystem, sample_document_result
    ):
        mock_documents_db.query.return_value = [sample_document_result]
        mock_filesystem.read_markdown.side_effect = FileNotFoundError("Not found")

        results = index_service.query_documents("test query")

        assert len(results) == 0

    def should_filter_documents_by_max_distance(self, index_service, mock_documents_db, mock_filesystem):
        far_result = QueryResult(
            document=VectorDocumentForStorage(
                id="doc1.md", content="Far document", metadata={"id": "doc1.md", "title": "Test"}
            ),
            distance=2.0,
        )
        mock_documents_db.query.return_value = [far_result]

        results = index_service.query_documents("test query", max_distance=1.0)

        assert len(results) == 0


class DescribeIndexServiceStats:
    """Tests for index statistics in IndexService."""

    @pytest.fixture
    def mock_tokenizer(self):
        return Mock(spec=TokenizerGateway)

    @pytest.fixture
    def mock_excerpts_db(self):
        return Mock(spec=VectorDatabase)

    @pytest.fixture
    def mock_documents_db(self):
        return Mock(spec=VectorDatabase)

    @pytest.fixture
    def mock_filesystem(self):
        return Mock(spec=MarkdownFilesystemGateway)

    @pytest.fixture
    def index_service(self, mock_tokenizer, mock_excerpts_db, mock_documents_db, mock_filesystem):
        return IndexService(
            tokenizer_gateway=mock_tokenizer,
            excerpts_db=mock_excerpts_db,
            documents_db=mock_documents_db,
            filesystem_gateway=mock_filesystem,
        )

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

    @pytest.fixture
    def mock_tokenizer(self):
        tokenizer = Mock(spec=TokenizerGateway)
        return tokenizer

    @pytest.fixture
    def mock_excerpts_db(self):
        return Mock(spec=VectorDatabase)

    @pytest.fixture
    def mock_documents_db(self):
        return Mock(spec=VectorDatabase)

    @pytest.fixture
    def mock_filesystem(self):
        return Mock(spec=MarkdownFilesystemGateway)

    @pytest.fixture
    def index_service(self, mock_tokenizer, mock_excerpts_db, mock_documents_db, mock_filesystem):
        return IndexService(
            tokenizer_gateway=mock_tokenizer,
            excerpts_db=mock_excerpts_db,
            documents_db=mock_documents_db,
            filesystem_gateway=mock_filesystem,
        )

    def should_split_large_documents_into_excerpts(
        self, index_service, mock_tokenizer, mock_excerpts_db, mock_filesystem
    ):
        # Create 1000 tokens that will be split into multiple excerpts
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
        mock_excerpts_db.add_documents.assert_called()

    def should_use_custom_excerpt_size_and_overlap(
        self, index_service, mock_tokenizer, mock_filesystem, mock_excerpts_db
    ):
        mock_tokenizer.encode.return_value = list(range(300))  # 300 tokens
        mock_tokenizer.decode.return_value = "decoded"
        mock_filesystem.read_markdown.return_value = ({"title": "Test"}, "Content")

        index_service.index_document("test.md", excerpt_size=100, excerpt_overlap=20)

        # With 300 tokens, 100 size, 20 overlap: should create multiple chunks
        assert mock_tokenizer.decode.call_count >= 3
