"""Factory for building the application service registry from configuration."""

import os

from mojentic.llm import LLMBroker
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import Config
from zk_chat.config_gateway import ConfigGateway
from zk_chat.gateway_factory import create_model_gateway
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.services.document_service import DocumentService
from zk_chat.services.index_service import IndexService
from zk_chat.services.link_traversal_service import LinkTraversalService
from zk_chat.services.service_registry import ServiceRegistry, ServiceType
from zk_chat.tools.git_gateway import GitGateway
from zk_chat.vector_database import VectorDatabase


def build_service_registry(config: Config) -> ServiceRegistry:
    """Build a fully-wired ServiceRegistry from configuration.

    Creates all core services (model gateway, chroma, vector databases, document
    service, index service, link traversal, LLM broker, smart memory, git gateway)
    and registers them in a ServiceRegistry.

    Parameters
    ----------
    config : Config
        The application configuration.

    Returns
    -------
    ServiceRegistry
        A fully populated service registry.
    """
    registry = ServiceRegistry()

    registry.register_service(ServiceType.CONFIG, config)

    config_gateway = ConfigGateway()
    registry.register_service(ServiceType.CONFIG_GATEWAY, config_gateway)

    global_config_gateway = GlobalConfigGateway()
    registry.register_service(ServiceType.GLOBAL_CONFIG_GATEWAY, global_config_gateway)

    gateway = create_model_gateway(config.gateway)
    registry.register_service(ServiceType.MODEL_GATEWAY, gateway)

    db_dir = os.path.join(config.vault, ".zk_chat_db")
    chroma_gateway = ChromaGateway(config.gateway, db_dir=db_dir)
    registry.register_service(ServiceType.CHROMA_GATEWAY, chroma_gateway)

    excerpts_db = VectorDatabase(
        chroma_gateway=chroma_gateway,
        gateway=gateway,
        collection_name=ZkCollectionName.EXCERPTS,
    )
    documents_db = VectorDatabase(
        chroma_gateway=chroma_gateway,
        gateway=gateway,
        collection_name=ZkCollectionName.DOCUMENTS,
    )

    filesystem_gateway = MarkdownFilesystemGateway(config.vault)
    registry.register_service(ServiceType.FILESYSTEM_GATEWAY, filesystem_gateway)

    tokenizer_gateway = TokenizerGateway()
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

    llm_broker = LLMBroker(config.model, gateway=gateway)
    registry.register_service(ServiceType.LLM_BROKER, llm_broker)

    smart_memory = SmartMemory(chroma_gateway=chroma_gateway, gateway=gateway)
    registry.register_service(ServiceType.SMART_MEMORY, smart_memory)

    git_gateway = GitGateway(config.vault)
    registry.register_service(ServiceType.GIT_GATEWAY, git_gateway)

    return registry
