import io
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
from mojentic.llm.gateways import OllamaGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway
from rich.console import Console

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import Config, ModelGateway
from zk_chat.config_gateway import ConfigGateway
from zk_chat.index import _full_reindex, _incremental_reindex, reindex
from zk_chat.index_resolution import ReindexDecision
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.progress_tracker import IndexingProgressTracker
from zk_chat.services.index_service import IndexService
from zk_chat.vector_database import VectorDatabase


@pytest.fixture
def config():
    return Config(vault="/test/vault", model="llama2", gateway=ModelGateway.OLLAMA, chunk_size=500, chunk_overlap=100)


@pytest.fixture
def index_service_setup():
    mock_chroma = Mock(spec=ChromaGateway)
    mock_ollama = Mock(spec=OllamaGateway)
    mock_tokenizer = Mock(spec=TokenizerGateway)
    mock_fs = Mock(spec=MarkdownFilesystemGateway)
    excerpts_db = VectorDatabase(mock_chroma, mock_ollama, ZkCollectionName.EXCERPTS)
    documents_db = VectorDatabase(mock_chroma, mock_ollama, ZkCollectionName.DOCUMENTS)
    service = IndexService(mock_tokenizer, excerpts_db, documents_db, mock_fs)
    return service, mock_fs


@pytest.fixture
def progress():
    return IndexingProgressTracker(console=Console(file=io.StringIO()))


class DescribeFullReindex:
    def should_call_reindex_all_with_config_params(self, config, index_service_setup, progress):
        index_service, mock_fs = index_service_setup
        mock_fs.iterate_markdown_files.return_value = iter([])

        with patch.object(index_service, "reindex_all", wraps=index_service.reindex_all) as spy:
            _full_reindex(config, index_service, progress)

        spy.assert_called_once()
        call_kwargs = spy.call_args.kwargs
        assert call_kwargs["excerpt_size"] == config.chunk_size
        assert call_kwargs["excerpt_overlap"] == config.chunk_overlap
        assert callable(call_kwargs["progress_callback"])

    def should_return_zero_counts_when_no_callback_invoked(self, config, index_service_setup, progress):
        index_service, mock_fs = index_service_setup
        mock_fs.iterate_markdown_files.return_value = iter([])

        files_processed, total_files = _full_reindex(config, index_service, progress)

        assert files_processed == 0
        assert total_files == 0

    def should_return_correct_counts_after_callback_invocations(self, config, index_service_setup, progress):
        index_service, mock_fs = index_service_setup
        mock_fs.iterate_markdown_files.return_value = iter(["file1.md", "file2.md"])
        mock_fs.read_markdown.return_value = ({}, "")

        files_processed, total_files = _full_reindex(config, index_service, progress)

        assert files_processed == 2
        assert total_files == 2

    def should_invoke_progress_callback_for_each_file(self, config, index_service_setup, progress):
        index_service, mock_fs = index_service_setup
        mock_fs.iterate_markdown_files.return_value = iter(["file1.md", "file2.md"])
        mock_fs.read_markdown.return_value = ({}, "")

        files_processed, _ = _full_reindex(config, index_service, progress)

        assert files_processed == 2


class DescribeIncrementalReindex:
    def should_call_update_index_with_config_params(self, config, index_service_setup, progress):
        index_service, mock_fs = index_service_setup
        last_indexed = datetime(2024, 1, 1)
        mock_fs.iterate_markdown_files.return_value = iter([])

        with patch.object(index_service, "update_index", wraps=index_service.update_index) as spy:
            _incremental_reindex(config, index_service, progress, last_indexed)

        spy.assert_called_once()
        call_kwargs = spy.call_args.kwargs
        assert call_kwargs["since"] == last_indexed
        assert call_kwargs["excerpt_size"] == config.chunk_size
        assert call_kwargs["excerpt_overlap"] == config.chunk_overlap
        assert callable(call_kwargs["progress_callback"])

    def should_return_zero_counts_when_no_callback_invoked(self, config, index_service_setup, progress):
        index_service, mock_fs = index_service_setup
        last_indexed = datetime(2024, 1, 1)
        mock_fs.iterate_markdown_files.return_value = iter([])

        files_processed, total_files = _incremental_reindex(config, index_service, progress, last_indexed)

        assert files_processed == 0
        assert total_files == 0

    def should_return_correct_counts_after_callbacks(self, config, index_service_setup, progress):
        index_service, mock_fs = index_service_setup
        last_indexed = datetime(2024, 1, 1)
        mock_fs.iterate_markdown_files.return_value = iter(["file1.md", "file2.md"])
        mock_fs.get_modified_time.return_value = datetime(2025, 1, 1)
        mock_fs.read_markdown.return_value = ({}, "")

        files_processed, total_files = _incremental_reindex(config, index_service, progress, last_indexed)

        assert files_processed == 2
        assert total_files == 2


class DescribeReindex:
    @pytest.fixture
    def mock_config_gateway(self):
        return Mock(spec=ConfigGateway)

    @pytest.fixture
    def real_index_service(self):
        mock_chroma = Mock(spec=ChromaGateway)
        mock_ollama = Mock(spec=OllamaGateway)
        mock_tokenizer = Mock(spec=TokenizerGateway)
        mock_fs = Mock(spec=MarkdownFilesystemGateway)
        mock_fs.iterate_markdown_files.return_value = iter([])
        excerpts_db = VectorDatabase(mock_chroma, mock_ollama, ZkCollectionName.EXCERPTS)
        documents_db = VectorDatabase(mock_chroma, mock_ollama, ZkCollectionName.DOCUMENTS)
        return IndexService(mock_tokenizer, excerpts_db, documents_db, mock_fs)

    def should_save_config_after_processing(self, config, mock_config_gateway, real_index_service):
        full_decision = ReindexDecision(strategy="full")

        with (
            patch("zk_chat.index.build_service_registry_with_defaults"),
            patch("zk_chat.index.ServiceProvider") as mock_provider_class,
            patch("zk_chat.index.determine_reindex_strategy", return_value=full_decision),
            patch("zk_chat.index.IndexingProgressTracker") as mock_tracker_class,
        ):
            mock_provider = mock_provider_class.return_value
            mock_provider.get_index_service.return_value = real_index_service

            mock_tracker = MagicMock()
            mock_tracker.__enter__ = Mock(return_value=mock_tracker)
            mock_tracker.__exit__ = Mock(return_value=False)
            mock_tracker_class.return_value = mock_tracker

            reindex(config, mock_config_gateway)

        mock_config_gateway.save.assert_called_once_with(config)

    def should_call_set_last_indexed_after_processing(self, config, mock_config_gateway, real_index_service):
        full_decision = ReindexDecision(strategy="full")

        with (
            patch("zk_chat.index.build_service_registry_with_defaults"),
            patch("zk_chat.index.ServiceProvider") as mock_provider_class,
            patch("zk_chat.index.determine_reindex_strategy", return_value=full_decision),
            patch("zk_chat.index.IndexingProgressTracker") as mock_tracker_class,
            patch.object(Config, "set_last_indexed") as mock_set_last_indexed,
        ):
            mock_provider = mock_provider_class.return_value
            mock_provider.get_index_service.return_value = real_index_service

            mock_tracker = MagicMock()
            mock_tracker.__enter__ = Mock(return_value=mock_tracker)
            mock_tracker.__exit__ = Mock(return_value=False)
            mock_tracker_class.return_value = mock_tracker

            reindex(config, mock_config_gateway)

        mock_set_last_indexed.assert_called_once()
        actual_timestamp = mock_set_last_indexed.call_args.args[0]
        assert isinstance(actual_timestamp, datetime)

    def should_dispatch_to_full_reindex_when_strategy_is_full(self, config, mock_config_gateway, real_index_service):
        full_decision = ReindexDecision(strategy="full")

        with (
            patch("zk_chat.index.build_service_registry_with_defaults"),
            patch("zk_chat.index.ServiceProvider") as mock_provider_class,
            patch("zk_chat.index.determine_reindex_strategy", return_value=full_decision),
            patch("zk_chat.index.IndexingProgressTracker") as mock_tracker_class,
            patch("zk_chat.index._full_reindex", return_value=(5, 5)) as mock_full_reindex,
            patch("zk_chat.index._incremental_reindex") as mock_incremental_reindex,
        ):
            mock_provider = mock_provider_class.return_value
            mock_provider.get_index_service.return_value = real_index_service

            mock_tracker = MagicMock()
            mock_tracker.__enter__ = Mock(return_value=mock_tracker)
            mock_tracker.__exit__ = Mock(return_value=False)
            mock_tracker_class.return_value = mock_tracker

            reindex(config, mock_config_gateway)

        mock_full_reindex.assert_called_once()
        mock_incremental_reindex.assert_not_called()

    def should_dispatch_to_incremental_reindex_when_strategy_is_incremental(
        self, config, mock_config_gateway, real_index_service
    ):
        last_indexed = datetime(2024, 6, 1)
        incremental_decision = ReindexDecision(strategy="incremental", last_indexed=last_indexed)

        with (
            patch("zk_chat.index.build_service_registry_with_defaults"),
            patch("zk_chat.index.ServiceProvider") as mock_provider_class,
            patch("zk_chat.index.determine_reindex_strategy", return_value=incremental_decision),
            patch("zk_chat.index.IndexingProgressTracker") as mock_tracker_class,
            patch("zk_chat.index._full_reindex") as mock_full_reindex,
            patch("zk_chat.index._incremental_reindex", return_value=(3, 3)) as mock_incremental_reindex,
        ):
            mock_provider = mock_provider_class.return_value
            mock_provider.get_index_service.return_value = real_index_service

            mock_tracker = MagicMock()
            mock_tracker.__enter__ = Mock(return_value=mock_tracker)
            mock_tracker.__exit__ = Mock(return_value=False)
            mock_tracker_class.return_value = mock_tracker

            reindex(config, mock_config_gateway)

        mock_incremental_reindex.assert_called_once()
        mock_full_reindex.assert_not_called()
