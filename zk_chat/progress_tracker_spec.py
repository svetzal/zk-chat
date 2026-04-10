"""Tests for progress tracking state management and callback logic."""

import io
from unittest.mock import MagicMock, patch

from rich.console import Console

from zk_chat.progress_tracker import IndexingProgressTracker, ProgressTracker


class DescribeProgressTracker:
    """Tests for ProgressTracker state management and public API."""

    def should_initialize_with_no_active_progress(self):
        tracker = ProgressTracker()

        assert tracker._progress is None
        assert tracker._main_task is None

    def should_accept_optional_console(self):
        console = Console(file=io.StringIO())

        tracker = ProgressTracker(console=console)

        assert tracker.console is console

    def should_create_default_console_when_none_provided(self):
        tracker = ProgressTracker()

        assert isinstance(tracker.console, Console)

    def should_start_progress_and_return_task_id(self):
        tracker = ProgressTracker()

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 42

            task_id = tracker.start_progress("Processing", total=10)

        assert task_id == 42
        mock_progress.start.assert_called_once()
        mock_progress.add_task.assert_called_once_with("Processing", total=10, current_file="")

    def should_stop_previous_session_when_starting_new_one(self):
        tracker = ProgressTracker()

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            first_progress = MagicMock()
            second_progress = MagicMock()
            mock_progress_class.side_effect = [first_progress, second_progress]
            first_progress.add_task.return_value = 1
            second_progress.add_task.return_value = 2

            tracker.start_progress("First")
            tracker.start_progress("Second")

        first_progress.stop.assert_called_once()

    def should_warn_and_return_when_updating_without_starting(self):
        tracker = ProgressTracker()

        tracker.update_progress(advance=1, current_file="test.md")

        assert tracker._progress is None

    def should_update_progress_with_advance(self):
        tracker = ProgressTracker()

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 1

            tracker.start_progress("Processing", total=100)
            tracker.update_progress(advance=1, current_file="notes/file.md")

        call_kwargs = mock_progress.update.call_args.kwargs
        assert call_kwargs["advance"] == 1

    def should_update_progress_with_completed(self):
        tracker = ProgressTracker()

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 1

            tracker.start_progress("Processing", total=100)
            tracker.update_progress(completed=50)

        call_kwargs = mock_progress.update.call_args.kwargs
        assert call_kwargs["completed"] == 50

    def should_set_total_on_active_progress(self):
        tracker = ProgressTracker()

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 1

            tracker.start_progress("Processing")
            tracker.set_total(100)

        mock_progress.update.assert_called_once_with(1, total=100)

    def should_warn_when_setting_total_without_starting(self):
        tracker = ProgressTracker()

        tracker.set_total(100)

        assert tracker._progress is None

    def should_stop_progress_and_reset_state(self):
        tracker = ProgressTracker()

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 1

            tracker.start_progress("Processing")
            tracker.stop_progress()

        mock_progress.stop.assert_called_once()
        assert tracker._progress is None
        assert tracker._main_task is None

    def should_work_as_context_manager(self):
        tracker = ProgressTracker()

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 1

            with tracker:
                tracker.start_progress("Processing")

        mock_progress.stop.assert_called_once()
        assert tracker._progress is None


class DescribeProgressTrackerCreateCallback:
    """Tests for the create_callback factory method."""

    def should_return_callable(self):
        tracker = ProgressTracker()

        callback = tracker.create_callback()

        assert callable(callback)

    def should_set_total_on_first_file(self):
        tracker = ProgressTracker()

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 1

            tracker.start_progress("Processing", total=None)
            callback = tracker.create_callback()
            callback("file.md", 1, 50)

        total_calls = [call for call in mock_progress.update.call_args_list if call.kwargs.get("total") is not None]
        assert len(total_calls) == 1
        assert total_calls[0].kwargs["total"] == 50

    def should_not_set_total_after_first_file(self):
        tracker = ProgressTracker()

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 1

            tracker.start_progress("Processing", total=None)
            callback = tracker.create_callback()
            callback("file1.md", 1, 50)
            callback("file2.md", 2, 50)

        total_setting_calls = [
            call for call in mock_progress.update.call_args_list if call.kwargs.get("total") is not None
        ]
        assert len(total_setting_calls) == 1

    def should_advance_by_one_for_processed_files(self):
        tracker = ProgressTracker()

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 1

            tracker.start_progress("Processing", total=10)
            callback = tracker.create_callback()
            callback("file.md", 1, 10)

        advance_calls = [call for call in mock_progress.update.call_args_list if call.kwargs.get("advance") == 1]
        assert len(advance_calls) == 1


class DescribeIndexingProgressTracker:
    """Tests for the IndexingProgressTracker specialized subclass."""

    def should_initialize_with_zero_last_processed_count(self):
        tracker = IndexingProgressTracker()

        assert tracker._last_processed_count == 0

    def should_start_scanning_with_indeterminate_total(self):
        tracker = IndexingProgressTracker()

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 1

            tracker.start_scanning()

        mock_progress.add_task.assert_called_once_with(
            "Scanning vault for markdown files...", total=None, current_file=""
        )

    def should_transition_from_scanning_to_processing(self):
        tracker = IndexingProgressTracker()

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 1

            tracker.start_scanning()
            tracker.finish_scanning(10)

        mock_progress.update.assert_called_once_with(
            1,
            description="Indexing 10 documents",
            total=10,
            completed=0,
            current_file="",
        )

    def should_reset_last_processed_count_on_finish_scanning(self):
        tracker = IndexingProgressTracker()
        tracker._last_processed_count = 5

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 1

            tracker.start_scanning()
            tracker.finish_scanning(10)

        assert tracker._last_processed_count == 0

    def should_update_file_processing_with_correct_advance(self):
        tracker = IndexingProgressTracker()
        tracker._last_processed_count = 2

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 1

            tracker.start_progress("Indexing", total=10)
            tracker.update_file_processing("notes/my-note.md", 5)

        advance_calls = [call for call in mock_progress.update.call_args_list if call.kwargs.get("advance") is not None]
        assert len(advance_calls) == 1
        assert advance_calls[0].kwargs["advance"] == 3

    def should_track_last_processed_count(self):
        tracker = IndexingProgressTracker()

        with patch("zk_chat.progress_tracker.Progress") as mock_progress_class:
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.add_task.return_value = 1

            tracker.start_progress("Indexing", total=10)
            tracker.update_file_processing("file1.md", 3)
            tracker.update_file_processing("file2.md", 7)

        assert tracker._last_processed_count == 7
