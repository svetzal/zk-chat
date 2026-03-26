"""Tests for the centralized default gateway factories."""

from zk_chat.config_gateway import ConfigGateway
from zk_chat.gateway_defaults import (
    create_default_config_gateway,
    create_default_global_config_gateway,
)
from zk_chat.global_config_gateway import GlobalConfigGateway


class DescribeCreateDefaultGlobalConfigGateway:
    def should_return_global_config_gateway_instance(self):
        result = create_default_global_config_gateway()

        assert isinstance(result, GlobalConfigGateway)


class DescribeCreateDefaultConfigGateway:
    def should_return_config_gateway_instance(self):
        result = create_default_config_gateway()

        assert isinstance(result, ConfigGateway)
