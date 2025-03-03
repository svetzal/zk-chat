from unittest.mock import Mock, ANY

from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.tools.retrieve_from_smart_memory import RetrieveFromSmartMemory


class DescribeRetrieveFromSmartMemory:
    """
    Describes the behavior of RetrieveFromSmartMemory tool which is responsible for
    retrieving relevant information from memory based on a query
    """

    def should_be_instantiated_with_smart_memory(self):
        mock_memory = Mock(spec=SmartMemory)

        tool = RetrieveFromSmartMemory(mock_memory)

        assert isinstance(tool, RetrieveFromSmartMemory)
        assert tool.memory == mock_memory

    def should_return_formatted_results_when_information_found(self):
        mock_memory = Mock(spec=SmartMemory)
        mock_memory.retrieve.return_value = {
            'documents': [['Test document 1'], ['Test document 2']],
            'distances': [[0.2], [0.5]]
        }
        tool = RetrieveFromSmartMemory(mock_memory)
        test_query = "test query"

        result = tool.run(test_query)

        mock_memory.retrieve.assert_called_once_with(test_query, ANY)
        assert "Found relevant information:" in result
        assert "1. [Relevance: 80.00%] Test document 1" in result
        assert "2. [Relevance: 50.00%] Test document 2" in result

    def should_return_no_results_message_when_nothing_found(self):
        mock_memory = Mock(spec=SmartMemory)
        mock_memory.retrieve.return_value = {'documents': [], 'distances': []}
        tool = RetrieveFromSmartMemory(mock_memory)
        test_query = "test query"

        result = tool.run(test_query)

        mock_memory.retrieve.assert_called_once_with(test_query, ANY)
        assert result == "No relevant information found in memory."
