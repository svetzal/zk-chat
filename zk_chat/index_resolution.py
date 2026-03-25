"""
Pure functions for index strategy resolution.

These functions contain no side effects and are fully testable without mocking I/O.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ReindexDecision(BaseModel):
    """
    Describes the reindex strategy to execute.

    Produced by determine_reindex_strategy; consumed by the reindex shell function.
    """

    model_config = ConfigDict(frozen=True)

    strategy: Literal["full", "incremental"]
    last_indexed: datetime | None = None


def determine_reindex_strategy(
    force_full: bool,
    last_indexed: datetime | None,
) -> ReindexDecision:
    """
    Determine whether to perform a full or incremental reindex.

    Parameters
    ----------
    force_full : bool
        Whether the caller explicitly requested a full reindex.
    last_indexed : datetime | None
        The timestamp of the last successful index run, or None if never indexed.

    Returns
    -------
    ReindexDecision
        Decision with strategy and (for incremental) the last_indexed timestamp.
    """
    if force_full or last_indexed is None:
        return ReindexDecision(strategy="full")
    return ReindexDecision(strategy="incremental", last_indexed=last_indexed)
