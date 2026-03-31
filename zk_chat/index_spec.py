from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from zk_chat.config import Config, ModelGateway
from zk_chat.config_gateway import ConfigGateway
from zk_chat.index import _full_reindex, _incremental_reindex, reindex
from zk_chat.index_resolution import ReindexDecision
from zk_chat.progress_tracker import IndexingProgressTracker
from zk_chat.services.index_service import IndexService


@pytest.fixture
def config():
    return Config(vault="/test/vault", model="llama2", gateway=ModelGateway.OLLAMA, chunk_size=500, chunk_overlap=100)


@pytest.fixture
def mock_index_service():
    return Mock(spec=IndexService)


@pytest.fixture
def mock_progress():
    return Mock(spec=IndexingProgressTracker)


class DescribeFullReindex:
    def should_call_start_scanning_on_progress(self, config, mock_index_service, mock_progress):
        _full_reindex(config, mock_index_service, mock_progress)

        mock_progress.start_scanning.assert_called_once_with()

    def should_call_reindex_all_with_config_params(self, config, mock_index_service, mock_progress):
        _full_reindex(config, mock_index_service, mock_progress)

        mock_index_service.reindex_all.assert_called_once()
        call_kwargs = mock_index_service.reindex_all.call_args.kwargs
        assert call_kwargs["excerpt_size"] == config.chunk_size
        assert call_kwargs["excerpt_overlap"] == config.chunk_overlap
        assert callable(call_kwargs["progress_callback"])

    def should_return_zero_counts_when_no_callback_invoked(self, config, mock_index_service, mock_progress):
        files_processed, total_files = _full_reindex(config, mock_index_service, mock_progress)

        assert files_processed == 0
        assert total_files == 0

    def should_call_finish_scanning_on_first_callback_invocation(self, config, mock_index_service, mock_progress):
        captured_callback = None

        def capture_callback(**kwargs):
            nonlocal captured_callback
            captured_callback = kwargs["progress_callback"]

        mock_index_service.reindex_all.side_effect = capture_callback

        _full_reindex(config, mock_index_service, mock_progress)
        captured_callback("file1.md", 1, 10)

        mock_progress.finish_scanning.assert_called_once_with(10)

    def should_call_update_file_processing_on_first_callback_invocation(
        self, config, mock_index_service, mock_progress
    ):
        captured_callback = None

        def capture_callback(**kwargs):
            nonlocal captured_callback
            captured_callback = kwargs["progress_callback"]

        mock_index_service.reindex_all.side_effect = capture_callback

        _full_reindex(config, mock_index_service, mock_progress)
        captured_callback("file1.md", 1, 10)

        mock_progress.update_file_processing.assert_called_once_with("file1.md", 1)

    def should_not_call_finish_scanning_on_subsequent_callback_invocations(
        self, config, mock_index_service, mock_progress
    ):
        captured_callback = None

        def capture_callback(**kwargs):
            nonlocal captured_callback
            captured_callback = kwargs["progress_callback"]

        mock_index_service.reindex_all.side_effect = capture_callback

        _full_reindex(config, mock_index_service, mock_progress)
        captured_callback("file1.md", 1, 10)
        captured_callback("file2.md", 2, 10)

        mock_progress.finish_scanning.assert_called_once_with(10)
        assert mock_progress.update_file_processing.call_count == 2

    def should_return_correct_counts_after_callback_invocations(self, config, mock_index_service, mock_progress):
        captured_callback = None

        def capture_callback(**kwargs):
            nonlocal captured_callback
            captured_callback = kwargs["progress_callback"]
            captured_callback("file1.md", 1, 5)
            captured_callback("file2.md", 2, 5)

        mock_index_service.reindex_all.side_effect = capture_callback

        files_processed, total_files = _full_reindex(config, mock_index_service, mock_progress)

        assert files_processed == 2
        assert total_files == 5


class DescribeIncrementalReindex:
    def should_call_start_scanning_with_modified_documents_message(
        self, config, mock_index_service, mock_progress
    ):
        last_indexed = datetime(2024, 1, 1)

        _incremental_reindex(config, mock_index_service, mock_progress, last_indexed)

        mock_progress.start_scanning.assert_called_once_with("Scanning for modified documents...")

    def should_call_update_index_with_config_params(self, config, mock_index_service, mock_progress):
        last_indexed = datetime(2024, 1, 1)

        _incremental_reindex(config, mock_index_service, mock_progress, last_indexed)

        mock_index_service.update_index.assert_called_once()
        call_kwargs = mock_index_service.update_index.call_args.kwargs
        assert call_kwargs["since"] == last_indexed
        assert call_kwargs["excerpt_size"] == config.chunk_size
        assert call_kwargs["excerpt_overlap"] == config.chunk_overlap
        assert callable(call_kwargs["progress_callback"])

    def should_return_zero_counts_when_no_callback_invoked(self, config, mock_index_service, mock_progress):
        last_indexed = datetime(2024, 1, 1)

        files_processed, total_files = _incremental_reindex(config, mock_index_service, mock_progress, last_indexed)

        assert files_processed == 0
        assert total_files == 0

    def should_call_update_progress_with_no_documents_message_when_total_count_is_zero(
        self, config, mock_index_service, mock_progress
    ):
        last_indexed = datetime(2024, 1, 1)
        captured_callback = None

        def capture_callback(**kwargs):
            nonlocal captured_callback
            captured_callback = kwargs["progress_callback"]

        mock_index_service.update_index.side_effect = capture_callback

        _incremental_reindex(config, mock_index_service, mock_progress, last_indexed)
        captured_callback("file1.md", 0, 0)

        mock_progress.update_progress.assert_called_once_with(description="No documents need updating")

    def should_not_call_update_file_processing_when_total_count_is_zero(
        self, config, mock_index_service, mock_progress
    ):
        last_indexed = datetime(2024, 1, 1)
        captured_callback = None

        def capture_callback(**kwargs):
            nonlocal captured_callback
            captured_callback = kwargs["progress_callback"]

        mock_index_service.update_index.side_effect = capture_callback

        _incremental_reindex(config, mock_index_service, mock_progress, last_indexed)
        captured_callback("file1.md", 0, 0)

        mock_progress.update_file_processing.assert_not_called()

    def should_call_finish_scanning_on_first_callback_with_nonzero_total(
        self, config, mock_index_service, mock_progress
    ):
        last_indexed = datetime(2024, 1, 1)
        captured_callback = None

        def capture_callback(**kwargs):
            nonlocal captured_callback
            captured_callback = kwargs["progress_callback"]

        mock_index_service.update_index.side_effect = capture_callback

        _incremental_reindex(config, mock_index_service, mock_progress, last_indexed)
        captured_callback("file1.md", 1, 3)

        mock_progress.finish_scanning.assert_called_once_with(3)

    def should_call_update_file_processing_on_callback_with_nonzero_total(
        self, config, mock_index_service, mock_progress
    ):
        last_indexed = datetime(2024, 1, 1)
        captured_callback = None

        def capture_callback(**kwargs):
            nonlocal captured_callback
            captured_callback = kwargs["progress_callback"]

        mock_index_service.update_index.side_effect = capture_callback

        _incremental_reindex(config, mock_index_service, mock_progress, last_indexed)
        captured_callback("file1.md", 1, 3)

        mock_progress.update_file_processing.assert_called_once_with("file1.md", 1)

    def should_return_correct_counts_after_callbacks(self, config, mock_index_service, mock_progress):
        last_indexed = datetime(2024, 1, 1)
        captured_callback = None

        def capture_callback(**kwargs):
            nonlocal captured_callback
            captured_callback = kwargs["progress_callback"]
            captured_callback("file1.md", 1, 3)
            captured_callback("file2.md", 2, 3)

        mock_index_service.update_index.side_effect = capture_callback

        files_processed, total_files = _incremental_reindex(config, mock_index_service, mock_progress, last_indexed)

        assert files_processed == 2
        assert total_files == 3


class DescribeReindex:
    @pytest.fixture
    def mock_config_gateway(self):
        return Mock(spec=ConfigGateway)

    def should_save_config_after_processing(self, config, mock_config_gateway):
        full_decision = ReindexDecision(strategy="full")

        with (
            patch("zk_chat.index.build_service_registry"),
            patch("zk_chat.index.ServiceProvider") as mock_provider_class,
            patch("zk_chat.index.determine_reindex_strategy", return_value=full_decision),
            patch("zk_chat.index.IndexingProgressTracker") as mock_tracker_class,
        ):
            mock_provider = mock_provider_class.return_value
            mock_provider.get_index_service.return_value = Mock(spec=IndexService)

            mock_tracker = MagicMock()
            mock_tracker.__enter__ = Mock(return_value=mock_tracker)
            mock_tracker.__exit__ = Mock(return_value=False)
            mock_tracker_class.return_value = mock_tracker

            reindex(config, mock_config_gateway)

        mock_config_gateway.save.assert_called_once_with(config)

    def should_call_set_last_indexed_after_processing(self, config, mock_config_gateway):
        full_decision = ReindexDecision(strategy="full")

        with (
            patch("zk_chat.index.build_service_registry"),
            patch("zk_chat.index.ServiceProvider") as mock_provider_class,
            patch("zk_chat.index.determine_reindex_strategy", return_value=full_decision),
            patch("zk_chat.index.IndexingProgressTracker") as mock_tracker_class,
            patch.object(Config, "set_last_indexed") as mock_set_last_indexed,
        ):
            mock_provider = mock_provider_class.return_value
            mock_provider.get_index_service.return_value = Mock(spec=IndexService)

            mock_tracker = MagicMock()
            mock_tracker.__enter__ = Mock(return_value=mock_tracker)
            mock_tracker.__exit__ = Mock(return_value=False)
            mock_tracker_class.return_value = mock_tracker

            reindex(config, mock_config_gateway)

        mock_set_last_indexed.assert_called_once()
        actual_timestamp = mock_set_last_indexed.call_args.args[0]
        assert isinstance(actual_timestamp, datetime)

    def should_dispatch_to_full_reindex_when_strategy_is_full(self, config, mock_config_gateway):
        full_decision = ReindexDecision(strategy="full")

        with (
            patch("zk_chat.index.build_service_registry"),
            patch("zk_chat.index.ServiceProvider") as mock_provider_class,
            patch("zk_chat.index.determine_reindex_strategy", return_value=full_decision),
            patch("zk_chat.index.IndexingProgressTracker") as mock_tracker_class,
            patch("zk_chat.index._full_reindex", return_value=(5, 5)) as mock_full_reindex,
            patch("zk_chat.index._incremental_reindex") as mock_incremental_reindex,
        ):
            mock_provider = mock_provider_class.return_value
            mock_index_service = Mock(spec=IndexService)
            mock_provider.get_index_service.return_value = mock_index_service

            mock_tracker = MagicMock()
            mock_tracker.__enter__ = Mock(return_value=mock_tracker)
            mock_tracker.__exit__ = Mock(return_value=False)
            mock_tracker_class.return_value = mock_tracker

            reindex(config, mock_config_gateway)

        mock_full_reindex.assert_called_once()
        mock_incremental_reindex.assert_not_called()

    def should_dispatch_to_incremental_reindex_when_strategy_is_incremental(self, config, mock_config_gateway):
        last_indexed = datetime(2024, 6, 1)
        incremental_decision = ReindexDecision(strategy="incremental", last_indexed=last_indexed)

        with (
            patch("zk_chat.index.build_service_registry"),
            patch("zk_chat.index.ServiceProvider") as mock_provider_class,
            patch("zk_chat.index.determine_reindex_strategy", return_value=incremental_decision),
            patch("zk_chat.index.IndexingProgressTracker") as mock_tracker_class,
            patch("zk_chat.index._full_reindex") as mock_full_reindex,
            patch("zk_chat.index._incremental_reindex", return_value=(3, 3)) as mock_incremental_reindex,
        ):
            mock_provider = mock_provider_class.return_value
            mock_index_service = Mock(spec=IndexService)
            mock_provider.get_index_service.return_value = mock_index_service

            mock_tracker = MagicMock()
            mock_tracker.__enter__ = Mock(return_value=mock_tracker)
            mock_tracker.__exit__ = Mock(return_value=False)
            mock_tracker_class.return_value = mock_tracker

            reindex(config, mock_config_gateway)

        mock_incremental_reindex.assert_called_once()
        mock_full_reindex.assert_not_called()
