from unittest.mock import Mock

import pytest

from zk_chat.console_service import RichConsoleService
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.tools.store_in_smart_memory import StoreInSmartMemory


@pytest.fixture
def mock_console_service():
    return Mock(spec=RichConsoleService)


class DescribeStoreInSmartMemory:
    """
    Describes the behavior of StoreInSmartMemory tool which is responsible for
    storing information in memory for later retrieval
    """

    def should_store_information_in_memory_and_return_confirmation(self, mock_console_service):
        mock_memory = Mock(spec=SmartMemory)
        tool = StoreInSmartMemory(mock_memory, mock_console_service)
        test_info = "test information to store"

        _ = tool.run(test_info)

        mock_memory.store.assert_called_once_with(test_info)
