from typing import TYPE_CHECKING, Any

import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from .service_provider import ServiceProvider
from .service_registry import ServiceType

if TYPE_CHECKING:
    from mojentic.llm import LLMBroker
    from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

    from zk_chat.chroma_gateway import ChromaGateway
    from zk_chat.config import Config
    from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
    from zk_chat.memory.smart_memory import SmartMemory
    from zk_chat.services.document_service import DocumentService
    from zk_chat.services.index_service import IndexService
    from zk_chat.services.link_traversal_service import LinkTraversalService
    from zk_chat.tools.git_gateway import GitGateway

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

    def __init__(self, service_provider: ServiceProvider) -> None:
        super().__init__()
        self._service_provider = service_provider
        self._logger = logger

    @property
    def service_provider(self) -> ServiceProvider:
        return self._service_provider

    @property
    def filesystem_gateway(self) -> "MarkdownFilesystemGateway | None":
        return self._service_provider.get_filesystem_gateway()

    @property
    def llm_broker(self) -> "LLMBroker | None":
        return self._service_provider.get_llm_broker()

    @property
    def document_service(self) -> "DocumentService | None":
        return self._service_provider.get_document_service()

    @property
    def index_service(self) -> "IndexService | None":
        return self._service_provider.get_index_service()

    @property
    def link_traversal_service(self) -> "LinkTraversalService | None":
        return self._service_provider.get_link_traversal_service()

    @property
    def smart_memory(self) -> "SmartMemory | None":
        return self._service_provider.get_smart_memory()

    @property
    def chroma_gateway(self) -> "ChromaGateway | None":
        return self._service_provider.get_chroma_gateway()

    @property
    def model_gateway(self) -> Any | None:
        return self._service_provider.get_model_gateway()

    @property
    def tokenizer_gateway(self) -> "TokenizerGateway | None":
        return self._service_provider.get_tokenizer_gateway()

    @property
    def git_gateway(self) -> "GitGateway | None":
        return self._service_provider.get_git_gateway()

    @property
    def config(self) -> "Config | None":
        return self._service_provider.get_config()

    @property
    def vault_path(self) -> str | None:
        """Absolute path to the current vault, or ``None`` when no vault config is loaded."""
        config = self.config
        return config.vault if config else None

    def require_service(self, service_type: ServiceType) -> Any:
        """Return the requested service, raising ``RuntimeError`` if it is not registered."""
        return self._service_provider.require_service(service_type)

    def has_service(self, service_type: ServiceType) -> bool:
        """Return ``True`` if the given service type is registered, ``False`` otherwise."""
        return self._service_provider.has_service(service_type)
