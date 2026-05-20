import io
from datetime import datetime
from unittest.mock import Mock, patch

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
from zk_chat.services.service_provider import ServiceProvider
from zk_chat.services.service_registry import ServiceRegistry, ServiceType
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
    def should_call_reindex_all_with_config_params(self, config, index_service_setup, progress, mock_console_gateway):
        index_service, mock_fs = index_service_setup
        mock_fs.iterate_markdown_files.return_value = iter([])

        with patch.object(index_service, "reindex_all", wraps=index_service.reindex_all) as spy:
            _full_reindex(config, index_service, progress, mock_console_gateway)

        spy.assert_called_once()
        call_kwargs = spy.call_args.kwargs
        assert call_kwargs["excerpt_size"] == config.chunk_size
        assert call_kwargs["excerpt_overlap"] == config.chunk_overlap
        assert callable(call_kwargs["progress_callback"])

    def should_return_zero_counts_when_no_callback_invoked(
        self, config, index_service_setup, progress, mock_console_gateway
    ):
        index_service, mock_fs = index_service_setup
        mock_fs.iterate_markdown_files.return_value = iter([])

        files_processed, total_files = _full_reindex(config, index_service, progress, mock_console_gateway)

        assert files_processed == 0
        assert total_files == 0

    def should_return_correct_counts_after_callback_invocations(
        self, config, index_service_setup, progress, mock_console_gateway
    ):
        index_service, mock_fs = index_service_setup
        mock_fs.iterate_markdown_files.return_value = iter(["file1.md", "file2.md"])
        mock_fs.read_markdown.return_value = ({}, "")

        files_processed, total_files = _full_reindex(config, index_service, progress, mock_console_gateway)

        assert files_processed == 2
        assert total_files == 2

    def should_invoke_progress_callback_for_each_file(
        self, config, index_service_setup, progress, mock_console_gateway
    ):
        index_service, mock_fs = index_service_setup
        mock_fs.iterate_markdown_files.return_value = iter(["file1.md", "file2.md"])
        mock_fs.read_markdown.return_value = ({}, "")

        files_processed, _ = _full_reindex(config, index_service, progress, mock_console_gateway)

        assert files_processed == 2

    def should_print_status_message(self, config, index_service_setup, progress, mock_console_gateway):
        index_service, mock_fs = index_service_setup
        mock_fs.iterate_markdown_files.return_value = iter([])

        _full_reindex(config, index_service, progress, mock_console_gateway)

        mock_console_gateway.print.assert_called_with("Performing full reindex...")


class DescribeIncrementalReindex:
    def should_call_update_index_with_config_params(self, config, index_service_setup, progress, mock_console_gateway):
        index_service, mock_fs = index_service_setup
        last_indexed = datetime(2024, 1, 1)
        mock_fs.iterate_markdown_files.return_value = iter([])

        with patch.object(index_service, "update_index", wraps=index_service.update_index) as spy:
            _incremental_reindex(config, index_service, progress, last_indexed, mock_console_gateway)

        spy.assert_called_once()
        call_kwargs = spy.call_args.kwargs
        assert call_kwargs["since"] == last_indexed
        assert call_kwargs["excerpt_size"] == config.chunk_size
        assert call_kwargs["excerpt_overlap"] == config.chunk_overlap
        assert callable(call_kwargs["progress_callback"])

    def should_return_zero_counts_when_no_callback_invoked(
        self, config, index_service_setup, progress, mock_console_gateway
    ):
        index_service, mock_fs = index_service_setup
        last_indexed = datetime(2024, 1, 1)
        mock_fs.iterate_markdown_files.return_value = iter([])

        files_processed, total_files = _incremental_reindex(
            config, index_service, progress, last_indexed, mock_console_gateway
        )

        assert files_processed == 0
        assert total_files == 0

    def should_return_correct_counts_after_callbacks(
        self, config, index_service_setup, progress, mock_console_gateway
    ):
        index_service, mock_fs = index_service_setup
        last_indexed = datetime(2024, 1, 1)
        mock_fs.iterate_markdown_files.return_value = iter(["file1.md", "file2.md"])
        mock_fs.get_modified_time.return_value = datetime(2025, 1, 1)
        mock_fs.read_markdown.return_value = ({}, "")

        files_processed, total_files = _incremental_reindex(
            config, index_service, progress, last_indexed, mock_console_gateway
        )

        assert files_processed == 2
        assert total_files == 2

    def should_print_status_message(self, config, index_service_setup, progress, mock_console_gateway):
        index_service, mock_fs = index_service_setup
        last_indexed = datetime(2024, 1, 1)
        mock_fs.iterate_markdown_files.return_value = iter([])

        _incremental_reindex(config, index_service, progress, last_indexed, mock_console_gateway)

        mock_console_gateway.print.assert_called_with(f"Performing incremental reindex since {last_indexed}...")


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

    def _make_provider(self, real_index_service):
        registry = ServiceRegistry()
        registry.register_service(ServiceType.INDEX_SERVICE, real_index_service)
        return ServiceProvider(registry)

    def _make_progress(self):
        return IndexingProgressTracker(console=Console(file=io.StringIO()))

    def should_save_config_after_processing(
        self, config, mock_config_gateway, real_index_service, mock_console_gateway
    ):
        full_decision = ReindexDecision(strategy="full")
        provider = self._make_provider(real_index_service)

        reindex(
            config,
            mock_config_gateway,
            console_gateway=mock_console_gateway,
            _provider_factory=lambda r: provider,
            _progress_factory=self._make_progress,
            _strategy_factory=lambda **kwargs: full_decision,
        )

        mock_config_gateway.save.assert_called_once_with(config)

    def should_call_set_last_indexed_after_processing(
        self, config, mock_config_gateway, real_index_service, mock_console_gateway
    ):
        full_decision = ReindexDecision(strategy="full")
        provider = self._make_provider(real_index_service)

        with patch.object(Config, "set_last_indexed") as mock_set_last_indexed:
            reindex(
                config,
                mock_config_gateway,
                console_gateway=mock_console_gateway,
                _provider_factory=lambda r: provider,
                _progress_factory=self._make_progress,
                _strategy_factory=lambda **kwargs: full_decision,
            )

        mock_set_last_indexed.assert_called_once()
        actual_timestamp = mock_set_last_indexed.call_args.args[0]
        assert isinstance(actual_timestamp, datetime)

    def should_dispatch_to_full_reindex_when_strategy_is_full(
        self, config, mock_config_gateway, real_index_service, mock_console_gateway
    ):
        full_decision = ReindexDecision(strategy="full")
        provider = self._make_provider(real_index_service)

        with (
            patch.object(real_index_service, "reindex_all", wraps=real_index_service.reindex_all) as spy_full,
            patch.object(real_index_service, "update_index", wraps=real_index_service.update_index) as spy_incremental,
        ):
            reindex(
                config,
                mock_config_gateway,
                console_gateway=mock_console_gateway,
                _provider_factory=lambda r: provider,
                _progress_factory=self._make_progress,
                _strategy_factory=lambda **kwargs: full_decision,
            )

        spy_full.assert_called_once()
        spy_incremental.assert_not_called()

    def should_dispatch_to_incremental_reindex_when_strategy_is_incremental(
        self, config, mock_config_gateway, real_index_service, mock_console_gateway
    ):
        last_indexed = datetime(2024, 6, 1)
        incremental_decision = ReindexDecision(strategy="incremental", last_indexed=last_indexed)
        provider = self._make_provider(real_index_service)

        with (
            patch.object(real_index_service, "reindex_all", wraps=real_index_service.reindex_all) as spy_full,
            patch.object(real_index_service, "update_index", wraps=real_index_service.update_index) as spy_incremental,
        ):
            reindex(
                config,
                mock_config_gateway,
                console_gateway=mock_console_gateway,
                _provider_factory=lambda r: provider,
                _progress_factory=self._make_progress,
                _strategy_factory=lambda **kwargs: incremental_decision,
            )

        spy_incremental.assert_called_once()
        spy_full.assert_not_called()
