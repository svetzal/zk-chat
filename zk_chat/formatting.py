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
    """Format a byte count as a human-readable KB/MB/GB string."""
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def categorize_index_age(last_indexed: datetime, now: datetime) -> IndexAge:
    """Staleness thresholds: >0 days = stale, >0 hours = hours_old, else fresh."""
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
    """Derive a ``VaultHealth`` summary from index recency and the number of markdown files."""
    if markdown_count == 0:
        return VaultHealth(status="no_files", message="No markdown files found in vault")
    if last_indexed is not None:
        return VaultHealth(status="healthy", message="Index appears healthy")
    return VaultHealth(status="needs_update", message="Index needs updating")


def truncate_for_display(text: str, max_length: int = 30) -> str:
    if len(text) > max_length:
        return text[: max_length - 3] + "..."
    return text


def extract_display_name(filepath: str) -> str:
    return filepath.split("/")[-1] if "/" in filepath else filepath


def calculate_advance(current_count: int, last_count: int) -> int:
    return current_count - last_count


def validate_progress_params(advance: int | None, completed: int | None) -> tuple[int | None, int | None]:
    """Ensure exactly one of ``advance`` / ``completed`` is set, defaulting ``advance`` to 1 when both are ``None``.

    Raises
    ------
    ValueError
        If both ``advance`` and ``completed`` are provided simultaneously.
    """
    if advance is not None and completed is not None:
        raise ValueError("Cannot specify both 'advance' and 'completed' parameters")
    if advance is None and completed is None:
        advance = 1
    return advance, completed
