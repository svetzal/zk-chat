"""
Tests for the iterative problem solving agent.

Tests for the strip_thinking utility function live in text_processing_spec.py.
"""

from unittest.mock import Mock

import pytest
from mojentic.llm import LLMBroker
from mojentic.llm.gateways import OllamaGateway
from mojentic.llm.gateways.models import LLMMessage, MessageRole

from zk_chat.iterative_problem_solving_agent import IterativeProblemSolvingAgent


def _response(content: str) -> LLMMessage:
    return LLMMessage(role=MessageRole.Assistant, content=content)


class DescribeIterativeProblemSolvingAgent:
    """Tests for the IterativeProblemSolvingAgent class."""

    @pytest.fixture
    def mock_gateway(self):
        return Mock(spec=OllamaGateway)

    @pytest.fixture
    def llm(self, mock_gateway):
        return LLMBroker(model="test", gateway=mock_gateway)

    @pytest.fixture
    def agent(self, llm):
        return IterativeProblemSolvingAgent(llm)

    def should_use_default_max_iterations_of_three(self, agent):
        assert agent.max_iterations == 3

    def should_stop_when_response_contains_done(self, agent, mock_gateway):
        mock_gateway.complete.side_effect = [
            _response("Task is DONE"),
            _response("Summary result"),
        ]

        result = agent.solve("solve this problem")

        assert result == "Summary result"
        assert mock_gateway.complete.call_count == 2

    def should_stop_when_response_contains_fail(self, agent, mock_gateway):
        mock_gateway.complete.side_effect = [
            _response("FAIL: cannot proceed"),
            _response("Summary after failure"),
        ]

        result = agent.solve("solve this problem")

        assert result == "Summary after failure"
        assert mock_gateway.complete.call_count == 2

    def should_stop_after_max_iterations_when_no_done_or_fail(self, llm, mock_gateway):
        agent = IterativeProblemSolvingAgent(llm, max_iterations=2)
        mock_gateway.complete.side_effect = [
            _response("Still working..."),
            _response("Still working..."),
            _response("Summary after max"),
        ]

        result = agent.solve("solve this problem")

        assert result == "Summary after max"
        assert mock_gateway.complete.call_count == 3

    def should_strip_thinking_blocks_before_evaluating_done(self, agent, mock_gateway):
        mock_gateway.complete.side_effect = [
            _response("<think>reasoning</think>DONE"),
            _response("Summary"),
        ]

        result = agent.solve("solve this problem")

        assert result == "Summary"
        assert mock_gateway.complete.call_count == 2

    def should_strip_thinking_blocks_before_evaluating_fail(self, agent, mock_gateway):
        mock_gateway.complete.side_effect = [
            _response("<think>reasoning</think>FAIL"),
            _response("Summary"),
        ]

        result = agent.solve("solve this problem")

        assert result == "Summary"
        assert mock_gateway.complete.call_count == 2

    def should_evaluate_done_case_insensitively(self, agent, mock_gateway):
        mock_gateway.complete.side_effect = [
            _response("done"),
            _response("Summary"),
        ]

        result = agent.solve("solve this problem")

        assert result == "Summary"
        assert mock_gateway.complete.call_count == 2

    def should_request_summary_after_solving(self, agent, mock_gateway):
        mock_gateway.complete.side_effect = [
            _response("DONE"),
            _response("Final summary"),
        ]

        agent.solve("solve this problem")

        last_call_messages = mock_gateway.complete.call_args_list[-1].kwargs["messages"]
        summary_request_content = last_call_messages[-2].content
        assert "Summarize" in summary_request_content
