"""Progress tracking for long-running operations using Rich library."""
from typing import Optional, Callable
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    SpinnerColumn,
    MofNCompleteColumn,
    TaskID
)
from rich.console import Console
import structlog

logger = structlog.get_logger()

ProgressCallback = Callable[[str, int, int], None]


class ProgressTracker:
    """
    Progress tracker for CLI operations using Rich library.

    Provides progress bars with file counts, processing rates, and current operation display.
    """

    def __init__(self, console: Optional[Console] = None):
        """Initialize progress tracker.

        Args:
            console: Optional Rich Console instance. Creates new one if None.
        """
        self.console = console or Console()
        self._progress: Optional[Progress] = None
        self._main_task: Optional[TaskID] = None
        self._current_operation = ""

    def start_progress(self, description: str = "Processing", total: Optional[int] = None) -> TaskID:
        """Start a new progress tracking session.

        Args:
            description: Description for the main progress bar
            total: Total number of items to process (None for indeterminate)

        Returns:
            TaskID for the main progress task
        """
        if self._progress is not None:
            logger.warning("Progress already started, stopping previous session")
            self.stop_progress()

        # Create progress with rich columns
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TextColumn("{task.fields[current_file]:<30}", style="cyan"),  # Fixed width filename
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            transient=False  # Keep progress visible after completion
        )

        self._progress.start()
        self._main_task = self._progress.add_task(description, total=total, current_file="")

        logger.info("Started progress tracking", description=description, total=total)
        return self._main_task

    def update_progress(self,
                       advance: Optional[int] = None,
                       completed: Optional[int] = None,
                       description: Optional[str] = None,
                       current_file: Optional[str] = None) -> None:
        """Update progress bar.

        Args:
            advance: Number of items to advance (mutually exclusive with completed)
            completed: Set absolute completed count (mutually exclusive with advance)
            description: Optional new description for progress bar
            current_file: Optional current file being processed
        """
        if self._progress is None or self._main_task is None:
            logger.warning("Progress not started, cannot update")
            return

        # Validate that only one of advance or completed is provided
        if advance is not None and completed is not None:
            raise ValueError("Cannot specify both 'advance' and 'completed' parameters")

        # Default to advance=1 if neither is provided
        if advance is None and completed is None:
            advance = 1

        # Build description without filename (filename goes in separate column)
        display_desc = description

        # Prepare filename for fixed-width column (truncate if too long, pad if too short)
        if current_file:
            if len(current_file) > 30:
                formatted_file = current_file[:27] + "..."
            else:
                formatted_file = current_file
        else:
            formatted_file = ""

        # Update with appropriate parameters
        update_kwargs = {
            "description": display_desc,
            "current_file": formatted_file
        }
        if advance is not None:
            update_kwargs["advance"] = advance
        elif completed is not None:
            update_kwargs["completed"] = completed

        self._progress.update(self._main_task, **update_kwargs)

    def set_total(self, total: int) -> None:
        """Set or update the total number of items.

        Args:
            total: Total number of items to process
        """
        if self._progress is None or self._main_task is None:
            logger.warning("Progress not started, cannot set total")
            return

        self._progress.update(self._main_task, total=total)
        logger.debug("Updated progress total", total=total)

    def stop_progress(self) -> None:
        """Stop the progress tracking session."""
        if self._progress is not None:
            self._progress.stop()
            self._progress = None
            self._main_task = None
            logger.info("Stopped progress tracking")

    def create_callback(self) -> ProgressCallback:
        """Create a progress callback function for use with other components.

        Returns:
            A callback function that can be passed to other methods
        """
        def callback(current_file: str, processed: int, total: int) -> None:
            if processed == 1:  # First file, set total if not already set
                self.set_total(total)
            self.update_progress(
                advance=1 if processed > 0 else 0,
                current_file=current_file
            )

        return callback

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure progress is stopped."""
        self.stop_progress()


class IndexingProgressTracker(ProgressTracker):
    """Specialized progress tracker for document indexing operations."""

    def __init__(self):
        super().__init__()
        self._last_processed_count = 0

    def start_scanning(self, description: str = "Scanning vault for markdown files...") -> None:
        """Start the file scanning phase."""
        self.start_progress(description, total=None)
        self._last_processed_count = 0

    def finish_scanning(self, file_count: int) -> None:
        """Transition from scanning to processing phase.

        Args:
            file_count: Total number of files found
        """
        if self._progress and self._main_task is not None:
            self._progress.update(
                self._main_task,
                description=f"Indexing {file_count} documents",
                total=file_count,
                completed=0,
                current_file=""
            )
            self._last_processed_count = 0

    def update_file_processing(self, filename: str, processed_count: int) -> None:
        """Update progress for file processing.

        Args:
            filename: Current file being processed
            processed_count: Number of files processed so far
        """
        # Extract just the filename from the path for cleaner display
        display_name = filename.split('/')[-1] if '/' in filename else filename

        # Calculate how much to advance since last update
        advance_by = processed_count - self._last_processed_count
        self._last_processed_count = processed_count

        self.update_progress(
            advance=advance_by,
            current_file=display_name
        )