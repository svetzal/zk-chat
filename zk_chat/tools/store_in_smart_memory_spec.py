from unittest.mock import Mock

import pytest
from mojentic.llm.gateways import OllamaGateway

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.console_service import ConsoleGateway
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.tools.store_in_smart_memory import StoreInSmartMemory


@pytest.fixture
def mock_console_service():
    return Mock(spec=ConsoleGateway)


@pytest.fixture
def mock_chroma():
    return Mock(spec=ChromaGateway)


@pytest.fixture
def mock_gateway():
    gateway = Mock(spec=OllamaGateway)
    gateway.calculate_embeddings.return_value = [0.1, 0.2, 0.3]
    return gateway


@pytest.fixture
def smart_memory(mock_chroma, mock_gateway):
    return SmartMemory(mock_chroma, mock_gateway)


class DescribeStoreInSmartMemory:
    """
    Describes the behavior of StoreInSmartMemory tool which is responsible for
    storing information in memory for later retrieval
    """

    def should_store_information_in_memory_and_return_confirmation(
        self, smart_memory, mock_chroma, mock_console_service
    ):
        tool = StoreInSmartMemory(smart_memory, mock_console_service)
        test_info = "test information to store"

        _ = tool.run(test_info)

        mock_chroma.add_items.assert_called_once()
        call_kwargs = mock_chroma.add_items.call_args.kwargs
        assert call_kwargs["documents"] == [test_info]
