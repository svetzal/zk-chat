import pytest

from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.tools.store_in_smart_memory import StoreInSmartMemory


@pytest.fixture
def smart_memory(mock_chroma_gateway, mock_ollama_gateway):
    return SmartMemory(mock_chroma_gateway, mock_ollama_gateway)


class DescribeStoreInSmartMemory:
    """
    Describes the behavior of StoreInSmartMemory tool which is responsible for
    storing information in memory for later retrieval
    """

    def should_store_information_in_memory_and_return_confirmation(
        self, smart_memory, mock_chroma_gateway, mock_console_service
    ):
        tool = StoreInSmartMemory(smart_memory, mock_console_service)
        test_info = "test information to store"

        _ = tool.run(test_info)

        mock_chroma_gateway.add_items.assert_called_once()
        call_kwargs = mock_chroma_gateway.add_items.call_args.kwargs
        assert call_kwargs["documents"] == [test_info]
