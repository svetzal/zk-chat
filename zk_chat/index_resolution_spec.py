"""
Tests for index_resolution pure functions.
"""

from datetime import datetime

from zk_chat.index_resolution import ReindexDecision, determine_reindex_strategy


class DescribeDetermineReindexStrategy:
    """Tests for the determine_reindex_strategy pure function."""

    def should_return_full_when_force_full_is_true(self):
        last_indexed = datetime(2026, 1, 1, 12, 0, 0)

        result = determine_reindex_strategy(force_full=True, last_indexed=last_indexed)

        assert result.strategy == "full"

    def should_return_full_when_last_indexed_is_none(self):
        result = determine_reindex_strategy(force_full=False, last_indexed=None)

        assert result.strategy == "full"

    def should_return_full_when_both_force_and_no_last_indexed(self):
        result = determine_reindex_strategy(force_full=True, last_indexed=None)

        assert result.strategy == "full"

    def should_return_incremental_when_not_forced_and_has_last_indexed(self):
        last_indexed = datetime(2026, 1, 1, 12, 0, 0)

        result = determine_reindex_strategy(force_full=False, last_indexed=last_indexed)

        assert result.strategy == "incremental"

    def should_pass_through_last_indexed_for_incremental(self):
        last_indexed = datetime(2026, 3, 15, 10, 30, 0)

        result = determine_reindex_strategy(force_full=False, last_indexed=last_indexed)

        assert result.last_indexed == last_indexed

    def should_have_none_last_indexed_for_full_strategy(self):
        result = determine_reindex_strategy(force_full=True, last_indexed=datetime(2026, 1, 1))

        assert result.last_indexed is None

    def should_return_correct_type(self):
        result = determine_reindex_strategy(force_full=False, last_indexed=None)

        assert isinstance(result, ReindexDecision)
