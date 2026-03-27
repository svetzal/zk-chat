"""
Tests for the iterative problem solving agent.

Tests for the strip_thinking utility function live in text_processing_spec.py.
"""

from unittest.mock import Mock, patch

import pytest
from mojentic.llm import ChatSession, LLMBroker

from zk_chat.iterative_problem_solving_agent import IterativeProblemSolvingAgent


class DescribeIterativeProblemSolvingAgent:
    """Tests for the IterativeProblemSolvingAgent class."""

    @pytest.fixture
    def mock_llm(self):
        return Mock(spec=LLMBroker)

    @pytest.fixture
    def mock_chat_instance(self):
        return Mock(spec=ChatSession)

    @pytest.fixture
    def agent(self, mock_llm, mock_chat_instance):
        with patch("zk_chat.iterative_problem_solving_agent.ChatSession") as mock_class:
            mock_class.return_value = mock_chat_instance
            yield IterativeProblemSolvingAgent(mock_llm)

    def should_use_default_max_iterations_of_three(self, agent):
        assert agent.max_iterations == 3

    def should_stop_when_response_contains_done(self, agent, mock_chat_instance):
        mock_chat_instance.send.side_effect = ["Task is DONE", "Summary result"]

        result = agent.solve("solve this problem")

        assert result == "Summary result"
        assert mock_chat_instance.send.call_count == 2

    def should_stop_when_response_contains_fail(self, agent, mock_chat_instance):
        mock_chat_instance.send.side_effect = ["FAIL: cannot proceed", "Summary after failure"]

        result = agent.solve("solve this problem")

        assert result == "Summary after failure"
        assert mock_chat_instance.send.call_count == 2

    def should_stop_after_max_iterations_when_no_done_or_fail(self, mock_llm, mock_chat_instance):
        with patch("zk_chat.iterative_problem_solving_agent.ChatSession") as mock_class:
            mock_class.return_value = mock_chat_instance
            agent = IterativeProblemSolvingAgent(mock_llm, max_iterations=2)

        mock_chat_instance.send.side_effect = ["Still working...", "Still working...", "Summary after max"]

        result = agent.solve("solve this problem")

        assert result == "Summary after max"
        assert mock_chat_instance.send.call_count == 3

    def should_strip_thinking_blocks_before_evaluating_done(self, agent, mock_chat_instance):
        mock_chat_instance.send.side_effect = ["<think>reasoning</think>DONE", "Summary"]

        result = agent.solve("solve this problem")

        assert result == "Summary"
        assert mock_chat_instance.send.call_count == 2

    def should_strip_thinking_blocks_before_evaluating_fail(self, agent, mock_chat_instance):
        mock_chat_instance.send.side_effect = ["<think>reasoning</think>FAIL", "Summary"]

        result = agent.solve("solve this problem")

        assert result == "Summary"
        assert mock_chat_instance.send.call_count == 2

    def should_evaluate_done_case_insensitively(self, agent, mock_chat_instance):
        mock_chat_instance.send.side_effect = ["done", "Summary"]

        result = agent.solve("solve this problem")

        assert result == "Summary"
        assert mock_chat_instance.send.call_count == 2

    def should_request_summary_after_solving(self, agent, mock_chat_instance):
        mock_chat_instance.send.side_effect = ["DONE", "Final summary"]

        agent.solve("solve this problem")

        last_call_arg = mock_chat_instance.send.call_args_list[-1][0][0]
        assert "Summarize" in last_call_arg
