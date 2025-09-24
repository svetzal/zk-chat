"""
Service provider for plugins to easily access services they need.

This provides a clean interface for plugins to request services without
needing to manage service discovery or handle service unavailability.
"""
from typing import Optional, Type, TypeVar
import structlog

from .service_registry import ServiceRegistry, ServiceType

logger = structlog.get_logger()

T = TypeVar('T')


class ServiceProvider:
    """
    Provider that plugins can use to access services.
    
    This provides a convenient interface for plugins to request services
    with proper error handling and logging.
    """
    
    def __init__(self, registry: ServiceRegistry):
        """
        Initialize the service provider with a service registry.
        
        Args:
            registry: The service registry to use for service lookup
        """
        self._registry = registry
        self._logger = logger
    
    def get_filesystem_gateway(self):
        """Get the filesystem gateway service."""
        from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
        return self._registry.get_service(ServiceType.FILESYSTEM_GATEWAY, MarkdownFilesystemGateway)
    
    def get_llm_broker(self):
        """Get the LLM broker service."""
        from mojentic.llm import LLMBroker
        return self._registry.get_service(ServiceType.LLM_BROKER, LLMBroker)
    
    def get_zettelkasten(self):
        """Get the Zettelkasten service."""
        from zk_chat.zettelkasten import Zettelkasten
        return self._registry.get_service(ServiceType.ZETTELKASTEN, Zettelkasten)
    
    def get_smart_memory(self):
        """Get the Smart Memory service."""
        from zk_chat.memory.smart_memory import SmartMemory
        return self._registry.get_service(ServiceType.SMART_MEMORY, SmartMemory)
    
    def get_chroma_gateway(self):
        """Get the ChromaDB gateway service."""
        from zk_chat.chroma_gateway import ChromaGateway
        return self._registry.get_service(ServiceType.CHROMA_GATEWAY, ChromaGateway)
    
    def get_model_gateway(self):
        """Get the underlying model gateway (Ollama/OpenAI)."""
        return self._registry.get_service(ServiceType.MODEL_GATEWAY)
    
    def get_tokenizer_gateway(self):
        """Get the tokenizer gateway service."""
        from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway
        return self._registry.get_service(ServiceType.TOKENIZER_GATEWAY, TokenizerGateway)
    
    def get_git_gateway(self):
        """Get the Git gateway service (may not be available)."""
        from zk_chat.tools.git_gateway import GitGateway
        return self._registry.get_service(ServiceType.GIT_GATEWAY, GitGateway)
    
    def get_config(self):
        """Get the application configuration."""
        from zk_chat.config import Config
        return self._registry.get_service(ServiceType.CONFIG, Config)
    
    def get_service(self, service_type: ServiceType, expected_type: Optional[Type[T]] = None) -> Optional[T]:
        """
        Generic method to get a service by type.
        
        Args:
            service_type: The type of service to retrieve
            expected_type: Optional type hint for better typing support
            
        Returns:
            The service instance if available, None otherwise
        """
        return self._registry.get_service(service_type, expected_type)
    
    def has_service(self, service_type: ServiceType) -> bool:
        """
        Check if a service is available.
        
        Args:
            service_type: The type of service to check
            
        Returns:
            True if the service is available, False otherwise
        """
        return self._registry.has_service(service_type)
    
    def require_service(self, service_type: ServiceType, expected_type: Optional[Type[T]] = None) -> T:
        """
        Get a required service and raise an exception if not available.
        
        Args:
            service_type: The type of service to retrieve
            expected_type: Optional type hint for better typing support
            
        Returns:
            The service instance
            
        Raises:
            RuntimeError: If the required service is not available
        """
        service = self._registry.get_service(service_type, expected_type)
        if service is None:
            raise RuntimeError(f"Required service {service_type.value} is not available")
        return service