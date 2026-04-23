"""Tests for DiagnosticService."""

from unittest.mock import Mock

import pytest

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.services.diagnostic_service import (
    CollectionSamples,
    CollectionStatus,
    DiagnosticService,
    EmbeddingTestResult,
)


@pytest.fixture
def mock_chroma():
    return Mock(spec=ChromaGateway)


@pytest.fixture
def service(mock_chroma):
    return DiagnosticService(mock_chroma)


class DescribeDiagnosticService:
    """Tests for the DiagnosticService component."""

    def should_be_instantiated_with_chroma_gateway(self, mock_chroma):
        svc = DiagnosticService(mock_chroma)

        assert isinstance(svc, DiagnosticService)

    class DescribeGetCollectionStatuses:
        def should_return_ok_status_for_non_empty_collection(self, service, mock_chroma):
            mock_collection = Mock()
            mock_collection.count.return_value = 42
            mock_chroma.get_collection.return_value = mock_collection

            statuses = service.get_collection_statuses()

            assert len(statuses) == 2
            assert all(isinstance(s, CollectionStatus) for s in statuses)
            assert all(s.count == 42 for s in statuses)
            assert all("OK" in s.status for s in statuses)

        def should_return_empty_status_for_empty_collection(self, service, mock_chroma):
            mock_collection = Mock()
            mock_collection.count.return_value = 0
            mock_chroma.get_collection.return_value = mock_collection

            statuses = service.get_collection_statuses()

            assert all(s.count == 0 for s in statuses)
            assert all("Empty" in s.status for s in statuses)

        def should_return_error_status_on_collection_failure(self, service, mock_chroma):
            mock_chroma.get_collection.side_effect = ValueError("collection not found")

            statuses = service.get_collection_statuses()

            assert len(statuses) == 2
            assert all("Error" in s.status for s in statuses)
            assert all(s.error is not None for s in statuses)

    class DescribeGetSampleDocuments:
        def should_return_samples_for_non_empty_collections(self, service, mock_chroma):
            mock_collection = Mock()
            mock_collection.count.return_value = 5
            mock_collection.get.return_value = {
                "ids": ["id1", "id2"],
                "metadatas": [{"title": "Doc One"}, {"title": "Doc Two"}],
                "documents": ["Content of document one", "Content of document two"],
            }
            mock_chroma.get_collection.return_value = mock_collection

            samples = service.get_sample_documents(limit=2)

            assert len(samples) == 2
            assert all(isinstance(s, CollectionSamples) for s in samples)
            assert samples[0].total_count == 5
            assert len(samples[0].entries) == 2
            assert samples[0].entries[0].title == "Doc One"

        def should_return_empty_entries_for_empty_collection(self, service, mock_chroma):
            mock_collection = Mock()
            mock_collection.count.return_value = 0
            mock_chroma.get_collection.return_value = mock_collection

            samples = service.get_sample_documents()

            assert all(s.total_count == 0 for s in samples)
            assert all(len(s.entries) == 0 for s in samples)

        def should_truncate_content_preview_to_100_chars(self, service, mock_chroma):
            long_content = "x" * 200
            mock_collection = Mock()
            mock_collection.count.return_value = 1
            mock_collection.get.return_value = {
                "ids": ["id1"],
                "metadatas": [{"title": "Test"}],
                "documents": [long_content],
            }
            mock_chroma.get_collection.return_value = mock_collection

            samples = service.get_sample_documents()

            assert samples[0].entries[0].content_preview == "x" * 100

    class DescribeTestEmbedding:
        def should_return_successful_result_when_embedding_generated(self, service):
            mock_gateway = Mock()
            mock_gateway.calculate_embeddings.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]

            result = service.test_embedding(mock_gateway, "test text")

            assert isinstance(result, EmbeddingTestResult)
            assert result.success is True
            assert result.dimensions == 5
            assert result.sample_values == [0.1, 0.2, 0.3]
            assert result.error is None

        def should_return_failure_result_on_connection_error(self, service):
            mock_gateway = Mock()
            mock_gateway.calculate_embeddings.side_effect = ConnectionError("connection refused")

            result = service.test_embedding(mock_gateway, "test text")

            assert result.success is False
            assert result.error == "connection refused"
            assert result.dimensions is None

        def should_return_failure_result_on_value_error(self, service):
            mock_gateway = Mock()
            mock_gateway.calculate_embeddings.side_effect = ValueError("bad input")

            result = service.test_embedding(mock_gateway, "test text")

            assert result.success is False
            assert "bad input" in result.error
