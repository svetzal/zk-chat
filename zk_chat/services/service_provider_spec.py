"""
Tests for the service provider system.
"""
from unittest.mock import Mock

from zk_chat.services.service_registry import ServiceRegistry, ServiceType
from zk_chat.services.service_provider import ServiceProvider


class DescribeServiceProvider:
    """Tests for the ServiceProvider class."""

    def should_be_instantiated_with_registry(self):
        registry = ServiceRegistry()
        
        provider = ServiceProvider(registry)
        
        assert isinstance(provider, ServiceProvider)

    def should_get_service_from_registry(self):
        registry = ServiceRegistry()
        mock_service = Mock()
        registry.register_service(ServiceType.LLM_BROKER, mock_service)
        provider = ServiceProvider(registry)
        
        retrieved_service = provider.get_service(ServiceType.LLM_BROKER)
        
        assert retrieved_service is mock_service

    def should_check_service_availability(self):
        registry = ServiceRegistry()
        mock_service = Mock()
        provider = ServiceProvider(registry)
        
        assert not provider.has_service(ServiceType.LLM_BROKER)
        
        registry.register_service(ServiceType.LLM_BROKER, mock_service)
        
        assert provider.has_service(ServiceType.LLM_BROKER)

    def should_require_service_successfully(self):
        registry = ServiceRegistry()
        mock_service = Mock()
        registry.register_service(ServiceType.LLM_BROKER, mock_service)
        provider = ServiceProvider(registry)
        
        retrieved_service = provider.require_service(ServiceType.LLM_BROKER)
        
        assert retrieved_service is mock_service

    def should_raise_error_for_required_unavailable_service(self):
        registry = ServiceRegistry()
        provider = ServiceProvider(registry)
        
        try:
            provider.require_service(ServiceType.LLM_BROKER)
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "Required service llm_broker is not available" in str(e)