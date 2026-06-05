from typing import TYPE_CHECKING, Any, TypeVar

import structlog

from .service_registry import ServiceRegistry, ServiceType

if TYPE_CHECKING:
    from mojentic.llm import LLMBroker
    from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

    from zk_chat.chroma_gateway import ChromaGateway
    from zk_chat.config import Config
    from zk_chat.config_gateway import ConfigGateway
    from zk_chat.console_gateway import ConsoleGateway
    from zk_chat.global_config_gateway import GlobalConfigGateway
    from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
    from zk_chat.memory.smart_memory import SmartMemory
    from zk_chat.services.diagnostic_service import DiagnosticService
    from zk_chat.services.document_service import DocumentService
    from zk_chat.services.index_service import IndexService
    from zk_chat.services.link_traversal_service import LinkTraversalService
    from zk_chat.services.mcp_service import MCPService
    from zk_chat.services.vault_status_service import VaultStatusService
    from zk_chat.tools.git_gateway import GitGateway

logger = structlog.get_logger()

T = TypeVar("T")


class ServiceProvider:
    """
    Provider that plugins can use to access services.

    This provides a convenient interface for plugins to request services
    with proper error handling and logging.
    """

    def __init__(self, registry: ServiceRegistry) -> None:
        self._registry = registry
        self._logger = logger

    def get_filesystem_gateway(self) -> "MarkdownFilesystemGateway | None":
        from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway

        return self._registry.get_service(ServiceType.FILESYSTEM_GATEWAY, MarkdownFilesystemGateway)

    def get_llm_broker(self) -> "LLMBroker | None":
        from mojentic.llm import LLMBroker

        return self._registry.get_service(ServiceType.LLM_BROKER, LLMBroker)

    def get_smart_memory(self) -> "SmartMemory | None":
        from zk_chat.memory.smart_memory import SmartMemory

        return self._registry.get_service(ServiceType.SMART_MEMORY, SmartMemory)

    def get_chroma_gateway(self) -> "ChromaGateway | None":
        from zk_chat.chroma_gateway import ChromaGateway

        return self._registry.get_service(ServiceType.CHROMA_GATEWAY, ChromaGateway)

    def get_model_gateway(self) -> Any | None:
        return self._registry.get_service(ServiceType.MODEL_GATEWAY)

    def get_tokenizer_gateway(self) -> "TokenizerGateway | None":
        from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

        return self._registry.get_service(ServiceType.TOKENIZER_GATEWAY, TokenizerGateway)

    def get_git_gateway(self) -> "GitGateway | None":
        from zk_chat.tools.git_gateway import GitGateway

        return self._registry.get_service(ServiceType.GIT_GATEWAY, GitGateway)

    def get_config(self) -> "Config | None":
        from zk_chat.config import Config

        return self._registry.get_service(ServiceType.CONFIG, Config)

    def get_config_gateway(self) -> "ConfigGateway | None":
        from zk_chat.config_gateway import ConfigGateway

        return self._registry.get_service(ServiceType.CONFIG_GATEWAY, ConfigGateway)

    def get_global_config_gateway(self) -> "GlobalConfigGateway | None":
        from zk_chat.global_config_gateway import GlobalConfigGateway

        return self._registry.get_service(ServiceType.GLOBAL_CONFIG_GATEWAY, GlobalConfigGateway)

    def get_document_service(self) -> "DocumentService | None":
        from zk_chat.services.document_service import DocumentService

        return self._registry.get_service(ServiceType.DOCUMENT_SERVICE, DocumentService)

    def get_index_service(self) -> "IndexService | None":
        from zk_chat.services.index_service import IndexService

        return self._registry.get_service(ServiceType.INDEX_SERVICE, IndexService)

    def get_link_traversal_service(self) -> "LinkTraversalService | None":
        from zk_chat.services.link_traversal_service import LinkTraversalService

        return self._registry.get_service(ServiceType.LINK_TRAVERSAL_SERVICE, LinkTraversalService)

    def get_console_gateway(self) -> "ConsoleGateway | None":
        from zk_chat.console_gateway import ConsoleGateway

        return self._registry.get_service(ServiceType.CONSOLE_GATEWAY, ConsoleGateway)

    def get_mcp_service(self) -> "MCPService | None":
        return self._registry.get_service(ServiceType.MCP_SERVICE)

    def get_vault_status_service(self) -> "VaultStatusService | None":
        return self._registry.get_service(ServiceType.VAULT_STATUS_SERVICE)

    def get_diagnostic_service(self) -> "DiagnosticService | None":
        return self._registry.get_service(ServiceType.DIAGNOSTIC_SERVICE)

    def get_service(self, service_type: ServiceType, expected_type: type[T] | None = None) -> T | None:
        """Look up a service by type, optionally asserting its concrete type.

        Parameters
        ----------
        service_type : ServiceType
            The registry key identifying the desired service.
        expected_type : type[T] | None
            When provided, the returned value is cast to this type for static analysis.

        Returns
        -------
        T | None
            The registered service instance, or ``None`` if not registered.
        """
        return self._registry.get_service(service_type, expected_type)

    def has_service(self, service_type: ServiceType) -> bool:
        """Return ``True`` if the given service type is registered, ``False`` otherwise."""
        return self._registry.has_service(service_type)

    def require_service(self, service_type: ServiceType, expected_type: type[T] | None = None) -> T:
        """Look up a service, raising ``RuntimeError`` when it is not registered.

        Parameters
        ----------
        service_type : ServiceType
            The registry key identifying the desired service.
        expected_type : type[T] | None
            When provided, the returned value is cast to this type for static analysis.

        Returns
        -------
        T
            The registered service instance.

        Raises
        ------
        RuntimeError
            If the service has not been registered in the underlying registry.
        """
        service = self._registry.get_service(service_type, expected_type)
        if service is None:
            raise RuntimeError(f"Required service {service_type.value} is not available")
        return service
