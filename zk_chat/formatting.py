"""Pure formatting and display logic functions.

These functions contain no I/O or side effects — they transform values
into display-ready strings or classify values into categories.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IndexAge(BaseModel):
    """Represents the age classification of a search index."""

    model_config = ConfigDict(frozen=True)

    category: str  # "stale", "hours_old", "fresh"
    description: str  # e.g., "3 day(s) ago - consider updating"


class VaultHealth(BaseModel):
    """Represents the health status of a vault's index."""

    model_config = ConfigDict(frozen=True)

    status: str  # "healthy", "no_files", "needs_update"
    message: str  # human-readable summary


def format_file_size(size_bytes: int) -> str:
    """Format a byte count as a human-readable string.

    Parameters
    ----------
    size_bytes : int
        Number of bytes to format.

    Returns
    -------
    str
        Human-readable size string (e.g., "1.5 KB", "3.2 MB", "1.1 GB").
    """
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def categorize_index_age(last_indexed: datetime, now: datetime) -> IndexAge:
    """Classify how stale a search index is relative to now.

    Parameters
    ----------
    last_indexed : datetime
        When the index was last updated.
    now : datetime
        The current datetime (passed in to keep function pure).

    Returns
    -------
    IndexAge
        IndexAge with category and human-readable description.
    """
    time_diff = now - last_indexed
    if time_diff.days > 0:
        return IndexAge(
            category="stale",
            description=f"{time_diff.days} day(s) ago - consider updating",
        )
    hours = time_diff.seconds // 3600
    if hours > 0:
        return IndexAge(
            category="hours_old",
            description=f"{hours} hour(s) ago - up to date",
        )
    return IndexAge(
        category="fresh",
        description="Recently updated",
    )


def assess_vault_health(last_indexed: datetime | None, markdown_count: int) -> VaultHealth:
    """Determine the health status of a vault's search index.

    Parameters
    ----------
    last_indexed : datetime | None
        When the index was last updated, or None if never indexed.
    markdown_count : int
        Number of markdown files in the vault.

    Returns
    -------
    VaultHealth
        VaultHealth with status and human-readable message.
    """
    if markdown_count == 0:
        return VaultHealth(status="no_files", message="No markdown files found in vault")
    if last_indexed is not None:
        return VaultHealth(status="healthy", message="Index appears healthy")
    return VaultHealth(status="needs_update", message="Index needs updating")


def truncate_for_display(text: str, max_length: int = 30) -> str:
    """Truncate a string to fit a fixed-width display column.

    Appends "..." when truncation occurs.

    Parameters
    ----------
    text : str
        String to potentially truncate.
    max_length : int
        Maximum allowed length (default 30).

    Returns
    -------
    str
        Original string if within limit, or truncated string with "..." suffix.
    """
    if len(text) > max_length:
        return text[: max_length - 3] + "..."
    return text


def extract_display_name(filepath: str) -> str:
    """Extract the filename portion from a filepath for cleaner display.

    Parameters
    ----------
    filepath : str
        Full or partial filepath string.

    Returns
    -------
    str
        The portion after the last "/" or the original string if no slashes.
    """
    return filepath.split("/")[-1] if "/" in filepath else filepath


def calculate_advance(current_count: int, last_count: int) -> int:
    """Calculate how much to advance a progress counter.

    Parameters
    ----------
    current_count : int
        The current processed item count.
    last_count : int
        The previously recorded processed item count.

    Returns
    -------
    int
        The delta between current and last counts.
    """
    return current_count - last_count


def validate_progress_params(
    advance: int | None, completed: int | None
) -> tuple[int | None, int | None]:
    """Validate and resolve progress update parameters.

    Advance and completed are mutually exclusive. When neither is provided,
    defaults to advance=1.

    Parameters
    ----------
    advance : int | None
        Number of items to advance (mutually exclusive with completed).
    completed : int | None
        Absolute completed count (mutually exclusive with advance).

    Returns
    -------
    tuple[int | None, int | None]
        Resolved (advance, completed) tuple.

    Raises
    ------
    ValueError
        If both advance and completed are provided.
    """
    if advance is not None and completed is not None:
        raise ValueError("Cannot specify both 'advance' and 'completed' parameters")
    if advance is None and completed is None:
        advance = 1
    return advance, completed
