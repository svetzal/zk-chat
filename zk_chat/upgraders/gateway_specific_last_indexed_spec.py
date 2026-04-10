from datetime import datetime
from unittest.mock import Mock

import pytest

from zk_chat.config import Config, ModelGateway
from zk_chat.config_gateway import ConfigGateway
from zk_chat.upgraders.gateway_specific_last_indexed import GatewaySpecificLastIndexed


@pytest.fixture
def config():
    return Config(vault="/test/vault", model="test", gateway=ModelGateway.OLLAMA)


@pytest.fixture
def mock_config_gateway():
    return Mock(spec=ConfigGateway)


@pytest.fixture
def upgrader(config, mock_config_gateway):
    return GatewaySpecificLastIndexed(config, mock_config_gateway)


class DescribeGatewaySpecificLastIndexed:
    def should_store_config_and_gateway_on_init(self, upgrader, config, mock_config_gateway):
        assert upgrader.config is config
        assert upgrader.config_gateway is mock_config_gateway

    class DescribeShouldRun:
        def should_return_true_when_last_indexed_set_and_no_gateway_last_indexed(
            self, config, mock_config_gateway
        ):
            config.last_indexed = datetime(2024, 1, 1)
            config.gateway_last_indexed = {}
            upgrader = GatewaySpecificLastIndexed(config, mock_config_gateway)

            assert upgrader.should_run() is True

        def should_return_false_when_last_indexed_is_none(self, config, mock_config_gateway):
            config.last_indexed = None
            config.gateway_last_indexed = {}
            upgrader = GatewaySpecificLastIndexed(config, mock_config_gateway)

            assert upgrader.should_run() is False

        def should_return_false_when_gateway_last_indexed_already_populated(
            self, config, mock_config_gateway
        ):
            config.last_indexed = datetime(2024, 1, 1)
            config.gateway_last_indexed = {"ollama": datetime(2024, 1, 1)}
            upgrader = GatewaySpecificLastIndexed(config, mock_config_gateway)

            assert upgrader.should_run() is False

        def should_return_false_when_both_last_indexed_none_and_gateway_last_indexed_empty(
            self, config, mock_config_gateway
        ):
            config.last_indexed = None
            config.gateway_last_indexed = {}
            upgrader = GatewaySpecificLastIndexed(config, mock_config_gateway)

            assert upgrader.should_run() is False

    class DescribeRun:
        def should_migrate_last_indexed_to_gateway_specific_storage(
            self, config, mock_config_gateway
        ):
            test_timestamp = datetime(2024, 6, 15, 12, 0, 0)
            config.last_indexed = test_timestamp
            upgrader = GatewaySpecificLastIndexed(config, mock_config_gateway)

            upgrader.run()

            assert config.gateway_last_indexed[ModelGateway.OLLAMA.value] == test_timestamp

        def should_save_config_via_gateway_after_migration(
            self, config, mock_config_gateway
        ):
            config.last_indexed = datetime(2024, 6, 15)
            upgrader = GatewaySpecificLastIndexed(config, mock_config_gateway)

            upgrader.run()

            mock_config_gateway.save.assert_called_once_with(config)

        def should_not_save_config_when_last_indexed_is_none(
            self, config, mock_config_gateway
        ):
            config.last_indexed = None
            upgrader = GatewaySpecificLastIndexed(config, mock_config_gateway)

            upgrader.run()

            mock_config_gateway.save.assert_not_called()
