from unittest.mock import ANY, Mock

import pytest

from zk_chat.console_service import RichConsoleService
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.tools.retrieve_from_smart_memory import RetrieveFromSmartMemory, format_memory_results


@pytest.fixture
def mock_console_service():
    return Mock(spec=RichConsoleService)


class DescribeFormatMemoryResults:
    """Tests for the format_memory_results pure function."""

    def should_return_no_results_message_when_all_distances_empty(self):
        result = format_memory_results([], [])

        assert result == "No relevant information found in memory."

    def should_return_no_results_message_when_distance_lists_are_empty(self):
        result = format_memory_results([["doc"]], [[]])

        assert result == "No relevant information found in memory."

    def should_convert_distance_to_relevance_percentage(self):
        result = format_memory_results([["Test document"]], [[0.2]])

        assert "80.00%" in result
        assert "Test document" in result

    def should_handle_zero_distance_as_100_percent_relevance(self):
        result = format_memory_results([["Perfect match"]], [[0.0]])

        assert "100.00%" in result

    def should_format_single_result_as_numbered_item(self):
        result = format_memory_results([["The content"]], [[0.5]])

        assert result.startswith("Found relevant information:\n1.")
        assert "50.00%" in result
        assert "The content" in result

    def should_format_multiple_results_as_numbered_list(self):
        result = format_memory_results(
            [["First doc"], ["Second doc"]],
            [[0.2], [0.5]],
        )

        assert "1. [Relevance: 80.00%] First doc" in result
        assert "2. [Relevance: 50.00%] Second doc" in result


class DescribeRetrieveFromSmartMemory:
    """
    Describes the behavior of RetrieveFromSmartMemory tool which is responsible for
    retrieving relevant information from memory based on a query
    """

    def should_be_instantiated_with_smart_memory(self, mock_console_service):
        mock_memory = Mock(spec=SmartMemory)

        tool = RetrieveFromSmartMemory(mock_memory, mock_console_service)

        assert isinstance(tool, RetrieveFromSmartMemory)
        assert tool.memory == mock_memory

    def should_return_formatted_results_when_information_found(self, mock_console_service):
        mock_memory = Mock(spec=SmartMemory)
        mock_memory.retrieve.return_value = {
            "documents": [["Test document 1"], ["Test document 2"]],
            "distances": [[0.2], [0.5]],
        }
        tool = RetrieveFromSmartMemory(mock_memory, mock_console_service)
        test_query = "test query"

        result = tool.run(test_query)

        mock_memory.retrieve.assert_called_once_with(test_query, ANY)
        assert "Found relevant information:" in result
        assert "1. [Relevance: 80.00%] Test document 1" in result
        assert "2. [Relevance: 50.00%] Test document 2" in result

    def should_return_no_results_message_when_nothing_found(self, mock_console_service):
        mock_memory = Mock(spec=SmartMemory)
        mock_memory.retrieve.return_value = {"documents": [], "distances": []}
        tool = RetrieveFromSmartMemory(mock_memory, mock_console_service)
        test_query = "test query"

        result = tool.run(test_query)

        mock_memory.retrieve.assert_called_once_with(test_query, ANY)
        assert result == "No relevant information found in memory."
