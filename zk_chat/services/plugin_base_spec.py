from unittest.mock import Mock

import pytest

from zk_chat.services.plugin_base import ZkChatPlugin
from zk_chat.services.service_provider import ServiceProvider
from zk_chat.services.service_registry import ServiceType


@pytest.fixture
def mock_service_provider():
    return Mock(spec=ServiceProvider)


@pytest.fixture
def plugin(mock_service_provider):
    return ZkChatPlugin(mock_service_provider)


class DescribeZkChatPlugin:
    """Tests for the ZkChatPlugin base class."""

    def should_be_instantiated_with_service_provider(self, mock_service_provider):
        plugin = ZkChatPlugin(mock_service_provider)

        assert isinstance(plugin, ZkChatPlugin)

    def should_expose_service_provider(self, plugin, mock_service_provider):
        assert plugin.service_provider is mock_service_provider

    class DescribeServiceProperties:
        """Tests for service accessor properties."""

        def should_delegate_filesystem_gateway_to_provider(self, plugin, mock_service_provider):
            _ = plugin.filesystem_gateway

            mock_service_provider.get_filesystem_gateway.assert_called_once()

        def should_delegate_llm_broker_to_provider(self, plugin, mock_service_provider):
            _ = plugin.llm_broker

            mock_service_provider.get_llm_broker.assert_called_once()

        def should_delegate_document_service_to_provider(self, plugin, mock_service_provider):
            _ = plugin.document_service

            mock_service_provider.get_document_service.assert_called_once()

        def should_delegate_index_service_to_provider(self, plugin, mock_service_provider):
            _ = plugin.index_service

            mock_service_provider.get_index_service.assert_called_once()

        def should_delegate_link_traversal_service_to_provider(self, plugin, mock_service_provider):
            _ = plugin.link_traversal_service

            mock_service_provider.get_link_traversal_service.assert_called_once()

        def should_delegate_smart_memory_to_provider(self, plugin, mock_service_provider):
            _ = plugin.smart_memory

            mock_service_provider.get_smart_memory.assert_called_once()

        def should_delegate_chroma_gateway_to_provider(self, plugin, mock_service_provider):
            _ = plugin.chroma_gateway

            mock_service_provider.get_chroma_gateway.assert_called_once()

        def should_delegate_model_gateway_to_provider(self, plugin, mock_service_provider):
            _ = plugin.model_gateway

            mock_service_provider.get_model_gateway.assert_called_once()

        def should_delegate_tokenizer_gateway_to_provider(self, plugin, mock_service_provider):
            _ = plugin.tokenizer_gateway

            mock_service_provider.get_tokenizer_gateway.assert_called_once()

        def should_delegate_git_gateway_to_provider(self, plugin, mock_service_provider):
            _ = plugin.git_gateway

            mock_service_provider.get_git_gateway.assert_called_once()

        def should_delegate_config_to_provider(self, plugin, mock_service_provider):
            _ = plugin.config

            mock_service_provider.get_config.assert_called_once()

    class DescribeVaultPath:
        """Tests for the vault_path property."""

        def should_return_vault_from_config_when_config_exists(self, plugin, mock_service_provider):
            mock_config = Mock()
            mock_config.vault = "/path/to/vault"
            mock_service_provider.get_config.return_value = mock_config

            result = plugin.vault_path

            assert result == "/path/to/vault"

        def should_return_none_when_config_is_none(self, plugin, mock_service_provider):
            mock_service_provider.get_config.return_value = None

            result = plugin.vault_path

            assert result is None

    class DescribeRequireService:
        """Tests for the require_service method."""

        def should_delegate_to_service_provider(self, plugin, mock_service_provider):
            mock_service = Mock()
            mock_service_provider.require_service.return_value = mock_service

            result = plugin.require_service(ServiceType.LLM_BROKER)

            mock_service_provider.require_service.assert_called_once_with(ServiceType.LLM_BROKER)
            assert result is mock_service

    class DescribeHasService:
        """Tests for the has_service method."""

        def should_return_true_when_service_is_available(self, plugin, mock_service_provider):
            mock_service_provider.has_service.return_value = True

            result = plugin.has_service(ServiceType.LLM_BROKER)

            mock_service_provider.has_service.assert_called_once_with(ServiceType.LLM_BROKER)
            assert result is True

        def should_return_false_when_service_is_not_available(self, plugin, mock_service_provider):
            mock_service_provider.has_service.return_value = False

            result = plugin.has_service(ServiceType.GIT_GATEWAY)

            mock_service_provider.has_service.assert_called_once_with(ServiceType.GIT_GATEWAY)
            assert result is False
