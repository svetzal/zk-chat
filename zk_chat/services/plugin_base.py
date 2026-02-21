"""
Base class for zk-chat plugins that provides convenient access to services.

This provides a clean interface for plugin developers while maintaining
backward compatibility and allowing for future extensibility.
"""

import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from .service_provider import ServiceProvider
from .service_registry import ServiceType

logger = structlog.get_logger()


class ZkChatPlugin(LLMTool):
    """
    Base class for zk-chat plugins that provides convenient service access.

    Plugin developers can inherit from this class to get easy access to
    all available services without needing to manage service discovery.

    Example:
        class MyPlugin(ZkChatPlugin):
            def __init__(self, service_provider: ServiceProvider):
                super().__init__(service_provider)

            def run(self, input_text: str) -> str:
                # Access services easily
                fs = self.filesystem_gateway
                llm = self.llm_broker
                docs = self.document_service

                # Your plugin logic here
                return "result"
    """

    def __init__(self, service_provider: ServiceProvider):
        """
        Initialize the plugin with a service provider.

        Args:
            service_provider: Service provider for accessing zk-chat services
        """
        super().__init__()
        self._service_provider = service_provider
        self._logger = logger

    @property
    def service_provider(self) -> ServiceProvider:
        """Get the service provider."""
        return self._service_provider

    # Convenient properties for accessing common services

    @property
    def filesystem_gateway(self):
        """Get the filesystem gateway for file operations."""
        return self._service_provider.get_filesystem_gateway()

    @property
    def llm_broker(self):
        """Get the LLM broker for making AI requests."""
        return self._service_provider.get_llm_broker()

    @property
    def document_service(self):
        """Get the DocumentService for document CRUD operations."""
        return self._service_provider.get_document_service()

    @property
    def index_service(self):
        """Get the IndexService for vector indexing and search operations."""
        return self._service_provider.get_index_service()

    @property
    def link_traversal_service(self):
        """Get the LinkTraversalService for wikilink analysis and graph traversal."""
        return self._service_provider.get_link_traversal_service()

    @property
    def smart_memory(self):
        """Get the Smart Memory service for long-term context."""
        return self._service_provider.get_smart_memory()

    @property
    def chroma_gateway(self):
        """Get the ChromaDB gateway for vector operations."""
        return self._service_provider.get_chroma_gateway()

    @property
    def model_gateway(self):
        """Get the underlying model gateway (Ollama/OpenAI)."""
        return self._service_provider.get_model_gateway()

    @property
    def tokenizer_gateway(self):
        """Get the tokenizer gateway."""
        return self._service_provider.get_tokenizer_gateway()

    @property
    def git_gateway(self):
        """Get the Git gateway (may be None if git is not enabled)."""
        return self._service_provider.get_git_gateway()

    @property
    def config(self):
        """Get the application configuration."""
        return self._service_provider.get_config()

    @property
    def vault_path(self) -> str | None:
        """Get the vault path from the configuration."""
        config = self.config
        return config.vault if config else None

    def require_service(self, service_type: ServiceType):
        """
        Get a required service and raise an exception if not available.

        Args:
            service_type: The type of service to retrieve

        Returns:
            The service instance

        Raises:
            RuntimeError: If the required service is not available
        """
        return self._service_provider.require_service(service_type)

    def has_service(self, service_type: ServiceType) -> bool:
        """
        Check if a service is available.

        Args:
            service_type: The type of service to check

        Returns:
            True if the service is available, False otherwise
        """
        return self._service_provider.has_service(service_type)
