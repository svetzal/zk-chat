"""Progress tracking for long-running operations using Rich library."""

from collections.abc import Callable
from typing import Self

import structlog
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

logger = structlog.get_logger()

ProgressCallback = Callable[[str, int, int], None]


class ProgressTracker:
    """Progress tracker for CLI operations using Rich library."""

    def __init__(
        self,
        console: Console | None = None,
        _progress_factory: Callable[..., Progress] | None = None,
    ) -> None:
        self.console = console or Console()
        self._progress_factory = _progress_factory
        self._progress: Progress | None = None
        self._main_task: TaskID | None = None
        self._current_operation = ""

    def start_progress(self, description: str = "Processing", total: int | None = None) -> TaskID:
        if self._progress is not None:
            logger.warning("Progress already started, stopping previous session")
            self.stop_progress()

        progress_cls = self._progress_factory or Progress
        self._progress = progress_cls(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TextColumn("{task.fields[current_file]:<30}", style="cyan"),  # Fixed width filename
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            transient=False,  # Keep progress visible after completion
        )

        self._progress.start()
        self._main_task = self._progress.add_task(description, total=total, current_file="")

        logger.info("Started progress tracking", description=description, total=total)
        return self._main_task

    def update_progress(
        self,
        advance: int | None = None,
        completed: int | None = None,
        description: str | None = None,
        current_file: str | None = None,
    ) -> None:
        if self._progress is None or self._main_task is None:
            logger.warning("Progress not started, cannot update")
            return

        from zk_chat.formatting import truncate_for_display, validate_progress_params

        advance, completed = validate_progress_params(advance, completed)

        display_desc = description
        formatted_file = truncate_for_display(current_file) if current_file else ""

        update_kwargs = {"description": display_desc, "current_file": formatted_file}
        if advance is not None:
            update_kwargs["advance"] = advance
        elif completed is not None:
            update_kwargs["completed"] = completed

        self._progress.update(self._main_task, **update_kwargs)

    def set_total(self, total: int) -> None:
        if self._progress is None or self._main_task is None:
            logger.warning("Progress not started, cannot set total")
            return

        self._progress.update(self._main_task, total=total)
        logger.debug("Updated progress total", total=total)

    def stop_progress(self) -> None:
        if self._progress is not None:
            self._progress.stop()
            self._progress = None
            self._main_task = None
            logger.info("Stopped progress tracking")

    def create_callback(self) -> ProgressCallback:
        def callback(current_file: str, processed: int, total: int) -> None:
            if processed == 1:  # First file, set total if not already set
                self.set_total(total)
            self.update_progress(advance=1 if processed > 0 else 0, current_file=current_file)

        return callback

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop_progress()


class IndexingProgressTracker(ProgressTracker):
    def __init__(
        self,
        console: Console | None = None,
        _progress_factory: Callable[..., Progress] | None = None,
    ) -> None:
        super().__init__(console=console, _progress_factory=_progress_factory)
        self._last_processed_count = 0

    def start_scanning(self, description: str = "Scanning vault for markdown files...") -> None:
        self.start_progress(description, total=None)
        self._last_processed_count = 0

    def finish_scanning(self, file_count: int) -> None:
        if self._progress and self._main_task is not None:
            self._progress.update(
                self._main_task,
                description=f"Indexing {file_count} documents",
                total=file_count,
                completed=0,
                current_file="",
            )
            self._last_processed_count = 0

    def update_file_processing(self, filename: str, processed_count: int) -> None:
        from zk_chat.formatting import calculate_advance, extract_display_name

        display_name = extract_display_name(filename)
        advance_by = calculate_advance(processed_count, self._last_processed_count)
        self._last_processed_count = processed_count

        self.update_progress(advance=advance_by, current_file=display_name)
