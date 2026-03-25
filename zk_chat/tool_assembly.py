"""
Tool assembly for the ZK Chat agent.

Assembles the full list of LLM tools from injected services.
This is a pure function: given services, it returns a deterministic tool list.
"""

from mojentic.llm import LLMBroker
from mojentic.llm.gateways import OllamaGateway, OpenAIGateway
from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic.llm.tools.date_resolver import ResolveDateTool
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.config import Config
from zk_chat.console_service import RichConsoleService
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.services.document_service import DocumentService
from zk_chat.services.index_service import IndexService
from zk_chat.services.link_traversal_service import LinkTraversalService
from zk_chat.tools.analyze_image import AnalyzeImage
from zk_chat.tools.commit_changes import CommitChanges
from zk_chat.tools.create_or_overwrite_zk_document import CreateOrOverwriteZkDocument
from zk_chat.tools.delete_zk_document import DeleteZkDocument
from zk_chat.tools.find_backlinks import FindBacklinks
from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo
from zk_chat.tools.find_forward_links import FindForwardLinks
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo
from zk_chat.tools.git_gateway import GitGateway
from zk_chat.tools.list_zk_documents import ListZkDocuments
from zk_chat.tools.list_zk_images import ListZkImages
from zk_chat.tools.read_zk_document import ReadZkDocument
from zk_chat.tools.rename_zk_document import RenameZkDocument
from zk_chat.tools.resolve_wikilink import ResolveWikiLink
from zk_chat.tools.retrieve_from_smart_memory import RetrieveFromSmartMemory
from zk_chat.tools.store_in_smart_memory import StoreInSmartMemory
from zk_chat.tools.uncommitted_changes import UncommittedChanges


def build_agent_tools(
    config: Config,
    filesystem_gateway: MarkdownFilesystemGateway,
    document_service: DocumentService,
    index_service: IndexService,
    link_traversal_service: LinkTraversalService,
    llm: LLMBroker,
    smart_memory: SmartMemory,
    git_gateway: GitGateway,
    gateway: OllamaGateway | OpenAIGateway,
    console_service: RichConsoleService,
) -> list[LLMTool]:
    """
    Assemble the complete list of tools for the ZK Chat agent.

    Parameters
    ----------
    config : Config
        Application configuration (vault path, visual model name, etc.)
    filesystem_gateway : MarkdownFilesystemGateway
        Gateway for filesystem operations on the vault
    document_service : DocumentService
        Service for document CRUD operations
    index_service : IndexService
        Service for vector index search operations
    link_traversal_service : LinkTraversalService
        Service for wikilink graph traversal
    llm : LLMBroker
        LLM broker used for commit message generation
    smart_memory : SmartMemory
        Persistent memory across chat sessions
    git_gateway : GitGateway
        Gateway for git operations (may be a no-op implementation)
    gateway : OllamaGateway | OpenAIGateway
        Raw model gateway used to create a visual LLM broker
    console_service : RichConsoleService
        Console service for tool status output

    Returns
    -------
    list[LLMTool]
        Fully constructed list of tools ready for the agent
    """
    visual_llm = LLMBroker(model=config.visual_model, gateway=gateway)
    return [
        # Real world context
        CurrentDateTimeTool(),
        ResolveDateTool(),
        # Document tools
        ReadZkDocument(document_service, console_service),
        ListZkDocuments(document_service, console_service),
        ListZkImages(filesystem_gateway, console_service),
        ResolveWikiLink(filesystem_gateway, console_service),
        FindExcerptsRelatedTo(index_service, console_service),
        FindZkDocumentsRelatedTo(index_service, console_service),
        CreateOrOverwriteZkDocument(document_service, console_service),
        RenameZkDocument(document_service, console_service),
        DeleteZkDocument(document_service, console_service),
        # Graph traversal tools
        FindBacklinks(link_traversal_service, console_service),
        FindForwardLinks(document_service, link_traversal_service, console_service),
        # Memory tools
        StoreInSmartMemory(smart_memory, console_service),
        RetrieveFromSmartMemory(smart_memory, console_service),
        # Visual tools
        AnalyzeImage(filesystem_gateway, visual_llm, console_service),
        # Git tools
        UncommittedChanges(config.vault, git_gateway, console_service),
        CommitChanges(config.vault, llm, git_gateway, console_service),
    ]
