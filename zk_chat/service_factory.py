"""Factory for building the application service registry from configuration."""

from mojentic.llm import LLMBroker
from mojentic.llm.gateways import OllamaGateway, OpenAIGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import Config
from zk_chat.config_gateway import ConfigGateway
from zk_chat.console_service import ConsoleGateway
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.services.document_service import DocumentService
from zk_chat.services.index_service import IndexService
from zk_chat.services.link_traversal_service import LinkTraversalService
from zk_chat.services.service_registry import ServiceRegistry, ServiceType
from zk_chat.tools.git_gateway import GitGateway
from zk_chat.vector_database import VectorDatabase


def build_service_registry(
    config: Config,
    config_gateway: ConfigGateway,
    global_config_gateway: GlobalConfigGateway,
    model_gateway: OllamaGateway | OpenAIGateway,
    chroma_gateway: ChromaGateway,
    filesystem_gateway: MarkdownFilesystemGateway,
    tokenizer_gateway: TokenizerGateway,
    git_gateway: GitGateway,
    console_service: ConsoleGateway,
) -> ServiceRegistry:
    """Build a fully-wired ServiceRegistry from injected gateways.

    All gateway instances must be pre-constructed and injected by the caller.
    Derived services (VectorDatabase, DocumentService, IndexService,
    LinkTraversalService, LLMBroker, SmartMemory) are built here from
    the injected gateways.

    Parameters
    ----------
    config : Config
        The application configuration.
    config_gateway : ConfigGateway
        Gateway for vault config I/O.
    global_config_gateway : GlobalConfigGateway
        Gateway for global config I/O.
    model_gateway : OllamaGateway | OpenAIGateway
        LLM model gateway.
    chroma_gateway : ChromaGateway
        ChromaDB gateway for vector storage.
    filesystem_gateway : MarkdownFilesystemGateway
        Gateway for markdown filesystem operations.
    tokenizer_gateway : TokenizerGateway
        Gateway for token counting.
    git_gateway : GitGateway
        Gateway for git operations.
    console_service : ConsoleGateway
        Gateway for console output.

    Returns
    -------
    ServiceRegistry
        A fully populated service registry.
    """
    registry = ServiceRegistry()

    registry.register_service(ServiceType.CONFIG, config)
    registry.register_service(ServiceType.CONFIG_GATEWAY, config_gateway)
    registry.register_service(ServiceType.GLOBAL_CONFIG_GATEWAY, global_config_gateway)
    registry.register_service(ServiceType.MODEL_GATEWAY, model_gateway)
    registry.register_service(ServiceType.CHROMA_GATEWAY, chroma_gateway)

    excerpts_db = VectorDatabase(
        chroma_gateway=chroma_gateway,
        gateway=model_gateway,
        collection_name=ZkCollectionName.EXCERPTS,
    )
    documents_db = VectorDatabase(
        chroma_gateway=chroma_gateway,
        gateway=model_gateway,
        collection_name=ZkCollectionName.DOCUMENTS,
    )

    registry.register_service(ServiceType.FILESYSTEM_GATEWAY, filesystem_gateway)
    registry.register_service(ServiceType.TOKENIZER_GATEWAY, tokenizer_gateway)

    document_service = DocumentService(filesystem_gateway)
    registry.register_service(ServiceType.DOCUMENT_SERVICE, document_service)

    index_service = IndexService(
        tokenizer_gateway=tokenizer_gateway,
        excerpts_db=excerpts_db,
        documents_db=documents_db,
        filesystem_gateway=filesystem_gateway,
    )
    registry.register_service(ServiceType.INDEX_SERVICE, index_service)

    link_traversal_service = LinkTraversalService(filesystem_gateway)
    registry.register_service(ServiceType.LINK_TRAVERSAL_SERVICE, link_traversal_service)

    llm_broker = LLMBroker(config.model, gateway=model_gateway)
    registry.register_service(ServiceType.LLM_BROKER, llm_broker)

    smart_memory = SmartMemory(chroma_gateway=chroma_gateway, gateway=model_gateway)
    registry.register_service(ServiceType.SMART_MEMORY, smart_memory)

    registry.register_service(ServiceType.GIT_GATEWAY, git_gateway)
    registry.register_service(ServiceType.CONSOLE_SERVICE, console_service)

    return registry


def build_service_registry_with_defaults(config: Config) -> ServiceRegistry:
    """Build a ServiceRegistry using all default gateways.

    Convenience wrapper that constructs all default gateway instances and
    calls build_service_registry. Use this at composition roots where no
    pre-built gateways are available.

    Parameters
    ----------
    config : Config
        The application configuration.

    Returns
    -------
    ServiceRegistry
        A fully populated service registry with default gateways.
    """
    from zk_chat.gateway_defaults import (
        create_default_chroma_gateway,
        create_default_config_gateway,
        create_default_console_gateway,
        create_default_filesystem_gateway,
        create_default_git_gateway,
        create_default_global_config_gateway,
        create_default_model_gateway,
        create_default_tokenizer_gateway,
    )

    return build_service_registry(
        config=config,
        config_gateway=create_default_config_gateway(),
        global_config_gateway=create_default_global_config_gateway(),
        model_gateway=create_default_model_gateway(config.gateway),
        chroma_gateway=create_default_chroma_gateway(config),
        filesystem_gateway=create_default_filesystem_gateway(config.vault),
        tokenizer_gateway=create_default_tokenizer_gateway(),
        git_gateway=create_default_git_gateway(config.vault),
        console_service=create_default_console_gateway(),
    )
