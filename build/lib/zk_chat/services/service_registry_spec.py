"""
Tests for the service registry system.
"""
from unittest.mock import Mock

from zk_chat.services.service_registry import ServiceRegistry, ServiceType


class DescribeServiceRegistry:
    """Tests for the ServiceRegistry class."""

    def should_be_instantiated(self):
        registry = ServiceRegistry()
        
        assert isinstance(registry, ServiceRegistry)

    def should_register_and_retrieve_service(self):
        registry = ServiceRegistry()
        mock_service = Mock()
        
        registry.register_service(ServiceType.LLM_BROKER, mock_service)
        retrieved_service = registry.get_service(ServiceType.LLM_BROKER)
        
        assert retrieved_service is mock_service

    def should_return_none_for_unregistered_service(self):
        registry = ServiceRegistry()
        
        retrieved_service = registry.get_service(ServiceType.LLM_BROKER)
        
        assert retrieved_service is None

    def should_check_service_availability(self):
        registry = ServiceRegistry()
        mock_service = Mock()
        
        assert not registry.has_service(ServiceType.LLM_BROKER)
        
        registry.register_service(ServiceType.LLM_BROKER, mock_service)
        
        assert registry.has_service(ServiceType.LLM_BROKER)

    def should_list_available_services(self):
        registry = ServiceRegistry()
        mock_service1 = Mock()
        mock_service2 = Mock()
        
        registry.register_service(ServiceType.LLM_BROKER, mock_service1)
        registry.register_service(ServiceType.FILESYSTEM_GATEWAY, mock_service2)
        
        available_services = registry.list_available_services()
        
        assert ServiceType.LLM_BROKER in available_services
        assert ServiceType.FILESYSTEM_GATEWAY in available_services
        assert len(available_services) == 2