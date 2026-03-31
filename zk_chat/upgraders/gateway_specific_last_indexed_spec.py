from datetime import datetime
from unittest.mock import Mock

import pytest

from zk_chat.config import Config, ModelGateway
from zk_chat.config_gateway import ConfigGateway
from zk_chat.upgraders.gateway_specific_last_indexed import GatewaySpecificLastIndexed


@pytest.fixture
def mock_config():
    return Mock(spec=Config)


@pytest.fixture
def mock_config_gateway():
    return Mock(spec=ConfigGateway)


@pytest.fixture
def upgrader(mock_config, mock_config_gateway):
    return GatewaySpecificLastIndexed(mock_config, mock_config_gateway)


class DescribeGatewaySpecificLastIndexed:
    def should_store_config_and_gateway_on_init(self, upgrader, mock_config, mock_config_gateway):
        assert upgrader.config is mock_config
        assert upgrader.config_gateway is mock_config_gateway

    class DescribeShouldRun:
        def should_return_true_when_last_indexed_set_and_no_gateway_last_indexed(
            self, upgrader, mock_config
        ):
            mock_config.last_indexed = datetime(2024, 1, 1)
            mock_config.gateway_last_indexed = {}

            assert upgrader.should_run() is True

        def should_return_false_when_last_indexed_is_none(self, upgrader, mock_config):
            mock_config.last_indexed = None
            mock_config.gateway_last_indexed = {}

            assert upgrader.should_run() is False

        def should_return_false_when_gateway_last_indexed_already_populated(
            self, upgrader, mock_config
        ):
            mock_config.last_indexed = datetime(2024, 1, 1)
            mock_config.gateway_last_indexed = {"ollama": datetime(2024, 1, 1)}

            assert upgrader.should_run() is False

        def should_return_false_when_both_last_indexed_none_and_gateway_last_indexed_empty(
            self, upgrader, mock_config
        ):
            mock_config.last_indexed = None
            mock_config.gateway_last_indexed = {}

            assert upgrader.should_run() is False

    class DescribeRun:
        def should_call_set_last_indexed_with_existing_timestamp(
            self, upgrader, mock_config, mock_config_gateway
        ):
            test_timestamp = datetime(2024, 6, 15, 12, 0, 0)
            mock_config.last_indexed = test_timestamp
            mock_config.gateway = ModelGateway.OLLAMA

            upgrader.run()

            mock_config.set_last_indexed.assert_called_once_with(test_timestamp)

        def should_save_config_via_gateway_after_migration(
            self, upgrader, mock_config, mock_config_gateway
        ):
            mock_config.last_indexed = datetime(2024, 6, 15)
            mock_config.gateway = ModelGateway.OLLAMA

            upgrader.run()

            mock_config_gateway.save.assert_called_once_with(mock_config)

        def should_not_call_set_last_indexed_when_last_indexed_is_none(
            self, upgrader, mock_config, mock_config_gateway
        ):
            mock_config.last_indexed = None

            upgrader.run()

            mock_config.set_last_indexed.assert_not_called()
            mock_config_gateway.save.assert_not_called()
