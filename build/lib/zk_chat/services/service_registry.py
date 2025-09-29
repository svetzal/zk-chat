"""
Service registry for managing available services for plugins.

This provides a type-safe way for plugins to request services without
needing to know about implementation details or requiring changes to
plugin constructors as new services are added.
"""
from enum import Enum
from typing import Any, Dict, Optional, Type, TypeVar
import structlog

logger = structlog.get_logger()

T = TypeVar('T')


class ServiceType(Enum):
    """Enumeration of available services that plugins can request."""
    
    # Core services
    FILESYSTEM_GATEWAY = "filesystem_gateway"
    LLM_BROKER = "llm_broker"
    ZETTELKASTEN = "zettelkasten"
    SMART_MEMORY = "smart_memory"
    
    # Database services
    CHROMA_GATEWAY = "chroma_gateway"
    VECTOR_DATABASE = "vector_database"
    
    # Gateway services
    MODEL_GATEWAY = "model_gateway"  # The underlying LLM gateway (Ollama/OpenAI)
    TOKENIZER_GATEWAY = "tokenizer_gateway"
    
    # Git services (when enabled)
    GIT_GATEWAY = "git_gateway"
    
    # Configuration
    CONFIG = "config"


class ServiceRegistry:
    """
    Registry that holds references to all available services.
    
    This allows plugins to request services by type without needing
    to know about specific implementations or requiring constructor
    parameter changes as new services are added.
    """
    
    def __init__(self):
        self._services: Dict[ServiceType, Any] = {}
        self._logger = logger
    
    def register_service(self, service_type: ServiceType, service_instance: Any) -> None:
        """
        Register a service instance for the given service type.
        
        Args:
            service_type: The type of service being registered
            service_instance: The actual service instance
        """
        self._services[service_type] = service_instance
        self._logger.info("Registered service", service_type=service_type.value)
    
    def get_service(self, service_type: ServiceType, expected_type: Optional[Type[T]] = None) -> Optional[T]:
        """
        Get a service instance by type.
        
        Args:
            service_type: The type of service to retrieve
            expected_type: Optional type hint for better typing support
            
        Returns:
            The service instance if available, None otherwise
        """
        service = self._services.get(service_type)
        if service is None:
            self._logger.warning("Service not available", service_type=service_type.value)
        return service
    
    def has_service(self, service_type: ServiceType) -> bool:
        """
        Check if a service is available.
        
        Args:
            service_type: The type of service to check
            
        Returns:
            True if the service is available, False otherwise
        """
        return service_type in self._services
    
    def list_available_services(self) -> list[ServiceType]:
        """
        Get a list of all available services.
        
        Returns:
            List of available service types
        """
        return list(self._services.keys())