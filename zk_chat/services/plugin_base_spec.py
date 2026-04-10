from unittest.mock import Mock

import pytest

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import Config, ModelGateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.services.document_service import DocumentService
from zk_chat.services.index_service import IndexService
from zk_chat.services.link_traversal_service import LinkTraversalService
from zk_chat.services.plugin_base import ZkChatPlugin
from zk_chat.services.service_provider import ServiceProvider
from zk_chat.services.service_registry import ServiceRegistry, ServiceType
from zk_chat.tools.git_gateway import GitGateway


def _make_registry(services: dict) -> ServiceRegistry:
    """Build a ServiceRegistry populated with the given ServiceType -> instance mappings."""
    registry = ServiceRegistry()
    for service_type, instance in services.items():
        registry.register_service(service_type, instance)
    return registry


@pytest.fixture
def registry():
    return ServiceRegistry()


@pytest.fixture
def service_provider(registry):
    return ServiceProvider(registry)


@pytest.fixture
def plugin(service_provider):
    return ZkChatPlugin(service_provider)


class DescribeZkChatPlugin:
    """Tests for the ZkChatPlugin base class."""

    def should_be_instantiated_with_service_provider(self, service_provider):
        plugin = ZkChatPlugin(service_provider)

        assert isinstance(plugin, ZkChatPlugin)

    def should_expose_service_provider(self, plugin, service_provider):
        assert plugin.service_provider is service_provider

    class DescribeServiceProperties:
        """Tests verifying the service accessor properties delegate through the provider."""

        def should_return_filesystem_gateway_when_registered(self):
            mock_fs = Mock(spec=MarkdownFilesystemGateway)
            registry = _make_registry({ServiceType.FILESYSTEM_GATEWAY: mock_fs})
            plugin = ZkChatPlugin(ServiceProvider(registry))

            result = plugin.filesystem_gateway

            assert result is mock_fs

        def should_return_none_for_filesystem_gateway_when_not_registered(self, plugin):
            assert plugin.filesystem_gateway is None

        def should_return_document_service_when_registered(self):
            mock_ds = Mock(spec=DocumentService)
            registry = _make_registry({ServiceType.DOCUMENT_SERVICE: mock_ds})
            plugin = ZkChatPlugin(ServiceProvider(registry))

            result = plugin.document_service

            assert result is mock_ds

        def should_return_index_service_when_registered(self):
            mock_is = Mock(spec=IndexService)
            registry = _make_registry({ServiceType.INDEX_SERVICE: mock_is})
            plugin = ZkChatPlugin(ServiceProvider(registry))

            result = plugin.index_service

            assert result is mock_is

        def should_return_link_traversal_service_when_registered(self):
            mock_lts = Mock(spec=LinkTraversalService)
            registry = _make_registry({ServiceType.LINK_TRAVERSAL_SERVICE: mock_lts})
            plugin = ZkChatPlugin(ServiceProvider(registry))

            result = plugin.link_traversal_service

            assert result is mock_lts

        def should_return_smart_memory_when_registered(self):
            mock_sm = Mock(spec=SmartMemory)
            registry = _make_registry({ServiceType.SMART_MEMORY: mock_sm})
            plugin = ZkChatPlugin(ServiceProvider(registry))

            result = plugin.smart_memory

            assert result is mock_sm

        def should_return_chroma_gateway_when_registered(self):
            mock_chroma = Mock(spec=ChromaGateway)
            registry = _make_registry({ServiceType.CHROMA_GATEWAY: mock_chroma})
            plugin = ZkChatPlugin(ServiceProvider(registry))

            result = plugin.chroma_gateway

            assert result is mock_chroma

        def should_return_git_gateway_when_registered(self):
            mock_git = Mock(spec=GitGateway)
            registry = _make_registry({ServiceType.GIT_GATEWAY: mock_git})
            plugin = ZkChatPlugin(ServiceProvider(registry))

            result = plugin.git_gateway

            assert result is mock_git

        def should_return_config_when_registered(self):
            config = Config(vault="/test/vault", model="test", gateway=ModelGateway.OLLAMA)
            registry = _make_registry({ServiceType.CONFIG: config})
            plugin = ZkChatPlugin(ServiceProvider(registry))

            result = plugin.config

            assert result is config

    class DescribeVaultPath:
        """Tests for the vault_path property."""

        def should_return_vault_from_config_when_config_exists(self):
            config = Config(vault="/path/to/vault", model="test", gateway=ModelGateway.OLLAMA)
            registry = _make_registry({ServiceType.CONFIG: config})
            plugin = ZkChatPlugin(ServiceProvider(registry))

            result = plugin.vault_path

            assert result == "/path/to/vault"

        def should_return_none_when_config_is_none(self, plugin):
            result = plugin.vault_path

            assert result is None

    class DescribeRequireService:
        """Tests for the require_service method."""

        def should_raise_when_service_not_registered(self, plugin):
            try:
                plugin.require_service(ServiceType.LLM_BROKER)
                raise AssertionError("Should have raised RuntimeError")
            except RuntimeError as e:
                assert "llm_broker" in str(e)

        def should_return_service_when_registered(self):
            mock_service = Mock()
            registry = _make_registry({ServiceType.LLM_BROKER: mock_service})
            plugin = ZkChatPlugin(ServiceProvider(registry))

            result = plugin.require_service(ServiceType.LLM_BROKER)

            assert result is mock_service

    class DescribeHasService:
        """Tests for the has_service method."""

        def should_return_true_when_service_is_available(self):
            mock_fs = Mock(spec=MarkdownFilesystemGateway)
            registry = _make_registry({ServiceType.FILESYSTEM_GATEWAY: mock_fs})
            plugin = ZkChatPlugin(ServiceProvider(registry))

            result = plugin.has_service(ServiceType.FILESYSTEM_GATEWAY)

            assert result is True

        def should_return_false_when_service_is_not_available(self, plugin):
            result = plugin.has_service(ServiceType.GIT_GATEWAY)

            assert result is False
