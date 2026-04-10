"""
Tests for the service provider system.
"""

from unittest.mock import Mock

from mojentic.llm import LLMBroker
from mojentic.llm.gateways import OllamaGateway

from zk_chat.config import Config, ModelGateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.services.service_provider import ServiceProvider
from zk_chat.services.service_registry import ServiceRegistry, ServiceType


class DescribeServiceProvider:
    """Tests for the ServiceProvider class."""

    def should_be_instantiated_with_registry(self):
        registry = ServiceRegistry()

        provider = ServiceProvider(registry)

        assert isinstance(provider, ServiceProvider)

    def should_get_service_from_registry(self):
        registry = ServiceRegistry()
        mock_service = Mock()  # Intentionally unspec'd: testing generic registry contract
        registry.register_service(ServiceType.LLM_BROKER, mock_service)
        provider = ServiceProvider(registry)

        retrieved_service = provider.get_service(ServiceType.LLM_BROKER)

        assert retrieved_service is mock_service

    def should_check_service_availability(self):
        registry = ServiceRegistry()
        mock_service = Mock()  # Intentionally unspec'd: testing generic registry contract
        provider = ServiceProvider(registry)

        assert not provider.has_service(ServiceType.LLM_BROKER)

        registry.register_service(ServiceType.LLM_BROKER, mock_service)

        assert provider.has_service(ServiceType.LLM_BROKER)

    def should_require_service_successfully(self):
        registry = ServiceRegistry()
        mock_service = Mock()  # Intentionally unspec'd: testing generic registry contract
        registry.register_service(ServiceType.LLM_BROKER, mock_service)
        provider = ServiceProvider(registry)

        retrieved_service = provider.require_service(ServiceType.LLM_BROKER)

        assert retrieved_service is mock_service

    def should_raise_error_for_required_unavailable_service(self):
        registry = ServiceRegistry()
        provider = ServiceProvider(registry)

        try:
            provider.require_service(ServiceType.LLM_BROKER)
            raise AssertionError("Should have raised RuntimeError")
        except RuntimeError as e:
            assert "Required service llm_broker is not available" in str(e)

    class DescribeTypedGetters:
        """Tests verifying the typed convenience getter methods delegate to the registry correctly."""

        def should_get_filesystem_gateway_by_type(self):
            registry = ServiceRegistry()
            mock_service = Mock(spec=MarkdownFilesystemGateway)
            registry.register_service(ServiceType.FILESYSTEM_GATEWAY, mock_service)
            provider = ServiceProvider(registry)

            result = provider.get_filesystem_gateway()

            assert result is mock_service

        def should_get_llm_broker_by_type(self):
            registry = ServiceRegistry()
            llm_broker = LLMBroker(model="test", gateway=Mock(spec=OllamaGateway))
            registry.register_service(ServiceType.LLM_BROKER, llm_broker)
            provider = ServiceProvider(registry)

            result = provider.get_llm_broker()

            assert result is llm_broker

        def should_get_config_by_type(self):
            registry = ServiceRegistry()
            config = Config(vault="/test/vault", model="test", gateway=ModelGateway.OLLAMA)
            registry.register_service(ServiceType.CONFIG, config)
            provider = ServiceProvider(registry)

            result = provider.get_config()

            assert result is config

        def should_return_none_when_typed_service_not_registered(self):
            registry = ServiceRegistry()
            provider = ServiceProvider(registry)

            result = provider.get_git_gateway()

            assert result is None
