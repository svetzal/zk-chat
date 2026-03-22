"""Specs for pure formatting and display logic functions."""

from datetime import datetime, timedelta

import pytest

from zk_chat.formatting import (
    IndexAge,
    VaultHealth,
    assess_vault_health,
    calculate_advance,
    categorize_index_age,
    extract_display_name,
    format_file_size,
    truncate_for_display,
    validate_progress_params,
)


class DescribeFormatFileSize:
    def should_format_bytes_below_1mb_as_kb(self):
        result = format_file_size(512 * 1024)

        assert result == "512.0 KB"

    def should_format_bytes_below_1gb_as_mb(self):
        result = format_file_size(3 * 1024 * 1024 + 205 * 1024)

        assert "MB" in result
        assert "3.2" in result

    def should_format_bytes_above_1gb_as_gb(self):
        result = format_file_size(2 * 1024 * 1024 * 1024)

        assert result == "2.0 GB"

    def should_handle_zero_bytes(self):
        result = format_file_size(0)

        assert result == "0.0 KB"

    def should_handle_exact_1mb_boundary(self):
        result = format_file_size(1024 * 1024)

        assert "MB" in result

    def should_handle_exact_1gb_boundary(self):
        result = format_file_size(1024 * 1024 * 1024)

        assert "GB" in result


class DescribeCategorizeIndexAge:
    def _now(self) -> datetime:
        return datetime(2024, 1, 15, 12, 0, 0)

    def should_return_stale_when_days_old(self):
        last_indexed = self._now() - timedelta(days=3)

        result = categorize_index_age(last_indexed, self._now())

        assert result.category == "stale"

    def should_include_day_count_in_description(self):
        last_indexed = self._now() - timedelta(days=3)

        result = categorize_index_age(last_indexed, self._now())

        assert "3 day(s) ago" in result.description

    def should_return_hours_old_when_over_one_hour(self):
        last_indexed = self._now() - timedelta(hours=2)

        result = categorize_index_age(last_indexed, self._now())

        assert result.category == "hours_old"

    def should_include_hour_count_in_description(self):
        last_indexed = self._now() - timedelta(hours=2)

        result = categorize_index_age(last_indexed, self._now())

        assert "2 hour(s) ago" in result.description

    def should_return_fresh_when_under_one_hour(self):
        last_indexed = self._now() - timedelta(minutes=15)

        result = categorize_index_age(last_indexed, self._now())

        assert result.category == "fresh"

    def should_return_index_age_model(self):
        last_indexed = self._now() - timedelta(days=1)

        result = categorize_index_age(last_indexed, self._now())

        assert isinstance(result, IndexAge)


class DescribeAssessVaultHealth:
    def should_return_healthy_when_indexed_and_has_files(self):
        last_indexed = datetime(2024, 1, 14, 10, 0, 0)

        result = assess_vault_health(last_indexed, markdown_count=10)

        assert result.status == "healthy"

    def should_return_no_files_when_markdown_count_is_zero(self):
        last_indexed = datetime(2024, 1, 14, 10, 0, 0)

        result = assess_vault_health(last_indexed, markdown_count=0)

        assert result.status == "no_files"

    def should_return_needs_update_when_never_indexed_but_has_files(self):
        result = assess_vault_health(None, markdown_count=5)

        assert result.status == "needs_update"

    def should_return_vault_health_model(self):
        result = assess_vault_health(None, markdown_count=0)

        assert isinstance(result, VaultHealth)

    def should_prioritize_no_files_over_never_indexed(self):
        result = assess_vault_health(None, markdown_count=0)

        assert result.status == "no_files"


class DescribeTruncateForDisplay:
    def should_return_text_unchanged_when_within_limit(self):
        result = truncate_for_display("short.md", max_length=30)

        assert result == "short.md"

    def should_truncate_with_ellipsis_when_exceeding_limit(self):
        long_name = "a" * 35

        result = truncate_for_display(long_name, max_length=30)

        assert len(result) == 30
        assert result.endswith("...")

    def should_handle_empty_string(self):
        result = truncate_for_display("")

        assert result == ""

    def should_handle_text_exactly_at_limit(self):
        text = "a" * 30

        result = truncate_for_display(text, max_length=30)

        assert result == text

    def should_respect_custom_max_length(self):
        result = truncate_for_display("hello world", max_length=8)

        assert result == "hello..."
        assert len(result) == 8


class DescribeExtractDisplayName:
    def should_extract_filename_from_path_with_slashes(self):
        result = extract_display_name("/home/user/notes/my-note.md")

        assert result == "my-note.md"

    def should_return_filename_when_no_slashes(self):
        result = extract_display_name("my-note.md")

        assert result == "my-note.md"

    def should_handle_empty_string(self):
        result = extract_display_name("")

        assert result == ""

    def should_handle_trailing_slash(self):
        result = extract_display_name("/home/user/notes/")

        assert result == ""


class DescribeCalculateAdvance:
    def should_return_difference_between_current_and_last(self):
        result = calculate_advance(current_count=10, last_count=7)

        assert result == 3

    def should_return_zero_when_counts_equal(self):
        result = calculate_advance(current_count=5, last_count=5)

        assert result == 0

    def should_return_one_for_single_increment(self):
        result = calculate_advance(current_count=6, last_count=5)

        assert result == 1


class DescribeValidateProgressParams:
    def should_raise_value_error_when_both_advance_and_completed_provided(self):
        with pytest.raises(ValueError, match="Cannot specify both"):
            validate_progress_params(advance=1, completed=5)

    def should_default_to_advance_1_when_neither_provided(self):
        advance, completed = validate_progress_params(None, None)

        assert advance == 1
        assert completed is None

    def should_pass_through_advance_when_only_advance_provided(self):
        advance, completed = validate_progress_params(advance=3, completed=None)

        assert advance == 3
        assert completed is None

    def should_pass_through_completed_when_only_completed_provided(self):
        advance, completed = validate_progress_params(advance=None, completed=10)

        assert advance is None
        assert completed == 10
