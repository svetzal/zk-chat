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
        mock_service = Mock()  # Intentionally unspec'd: testing generic registry contract

        registry.register_service(ServiceType.LLM_BROKER, mock_service)
        retrieved_service = registry.get_service(ServiceType.LLM_BROKER)

        assert retrieved_service is mock_service

    def should_return_none_for_unregistered_service(self):
        registry = ServiceRegistry()

        retrieved_service = registry.get_service(ServiceType.LLM_BROKER)

        assert retrieved_service is None

    def should_check_service_availability(self):
        registry = ServiceRegistry()
        mock_service = Mock()  # Intentionally unspec'd: testing generic registry contract

        assert not registry.has_service(ServiceType.LLM_BROKER)

        registry.register_service(ServiceType.LLM_BROKER, mock_service)

        assert registry.has_service(ServiceType.LLM_BROKER)

