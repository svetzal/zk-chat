"""Tests for the text_processing module."""

from zk_chat.text_processing import strip_thinking


class DescribeStripThinking:
    """Tests for the strip_thinking pure function."""

    def should_return_empty_string_for_empty_input(self):
        result = strip_thinking("")

        assert result == ""

    def should_return_text_unchanged_when_no_think_blocks(self):
        result = strip_thinking("Hello world")

        assert result == "Hello world"

    def should_remove_single_think_block(self):
        result = strip_thinking("<think>internal reasoning</think>result")

        assert result == "result"

    def should_remove_multiple_think_blocks(self):
        result = strip_thinking("<think>a</think>text<think>b</think>more")

        assert result == "textmore"

    def should_remove_multiline_think_blocks(self):
        result = strip_thinking("<think>\nreasoning\nacross lines\n</think>actual result")

        assert result == "actual result"

    def should_strip_leading_and_trailing_whitespace(self):
        result = strip_thinking("  <think>x</think>  result  ")

        assert result == "result"

    def should_preserve_text_before_and_after_think_blocks(self):
        result = strip_thinking("before<think>x</think>after")

        assert result == "beforeafter"

    def should_handle_text_that_is_only_a_think_block(self):
        result = strip_thinking("<think>everything</think>")

        assert result == ""

    def should_handle_closing_tag_only_without_opening_tag(self):
        """The string-split approach in the old commit_changes code only handled </think>.
        strip_thinking correctly ignores a lone closing tag."""
        result = strip_thinking("before</think>after")

        assert result == "before</think>after"
