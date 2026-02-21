# ruff: noqa: E402  # Configure logging/env before imports to reduce noisy logs and disable telemetry
import logging

logging.basicConfig(level=logging.WARN)

import os
from contextlib import contextmanager

from zk_chat.mcp_tool_wrapper import MCPClientManager

# Disable ChromaDB telemetry to avoid PostHog compatibility issues
os.environ["CHROMA_TELEMETRY"] = "false"
from pathlib import Path

from mojentic.llm import LLMBroker
from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic.llm.tools.date_resolver import ResolveDateTool
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.config import Config
from zk_chat.console_service import RichConsoleService
from zk_chat.iterative_problem_solving_agent import IterativeProblemSolvingAgent
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.mcp_client import verify_all_mcp_servers
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.service_factory import build_service_registry
from zk_chat.services.document_service import DocumentService
from zk_chat.services.index_service import IndexService
from zk_chat.services.link_traversal_service import LinkTraversalService
from zk_chat.services.service_provider import ServiceProvider
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


def _build_tools(
    config: Config,
    filesystem_gateway: MarkdownFilesystemGateway,
    document_service: DocumentService,
    index_service: IndexService,
    link_traversal_service: LinkTraversalService,
    llm,
    smart_memory: SmartMemory,
    git_gateway: GitGateway,
    gateway,
    console_service: RichConsoleService,
) -> list[LLMTool]:
    tools: list[LLMTool] = [
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
        AnalyzeImage(filesystem_gateway, LLMBroker(model=config.visual_model, gateway=gateway), console_service),
        # Git tools
        UncommittedChanges(config.vault, git_gateway, console_service),
        CommitChanges(config.vault, llm, git_gateway, console_service),
    ]
    return tools


@contextmanager
def _create_agent(config: Config):
    """Build a fully-wired IterativeProblemSolvingAgent from config."""
    registry = build_service_registry(config)
    provider = ServiceProvider(registry)

    tools = _build_tools(
        config=config,
        filesystem_gateway=provider.get_filesystem_gateway(),
        document_service=provider.get_document_service(),
        index_service=provider.get_index_service(),
        link_traversal_service=provider.get_link_traversal_service(),
        llm=provider.get_llm_broker(),
        smart_memory=provider.get_smart_memory(),
        git_gateway=provider.get_git_gateway(),
        gateway=provider.get_model_gateway(),
        console_service=provider.get_console_service(),
    )

    with MCPClientManager() as mcp_manager:
        tools.extend(mcp_manager.get_tools())

        agent_prompt_path = Path(__file__).parent / "agent_prompt.txt"
        with open(agent_prompt_path) as f:
            agent_prompt = f.read()

        yield IterativeProblemSolvingAgent(
            llm=provider.get_llm_broker(),
            available_tools=tools,
            system_prompt=agent_prompt,
        )


def agent(config: Config):
    from zk_chat.global_config_gateway import GlobalConfigGateway

    global_config = GlobalConfigGateway().load()
    if global_config.list_mcp_servers():
        print("Verifying MCP server availability...")
        unavailable = verify_all_mcp_servers()
        if unavailable:
            print("\nWarning: The following MCP servers are unavailable:")
            for name in unavailable:
                print(f"  - {name}")
            print("\nYou can continue, but these servers will not be accessible during the session.")
            print("Use 'zk-chat mcp verify' to check server status or 'zk-chat mcp list' to see all servers.\n")

    with _create_agent(config) as solver:
        while True:
            query = input("Agent request: ")
            if not query:
                break
            else:
                response = solver.solve(query)
                print(response)


def agent_single_query(config: Config, query: str) -> str:
    """
    Execute a single query using the agent and return the response.

    Parameters
    ----------
    config : Config
        Configuration object
    query : str
        The query string to process

    Returns
    -------
    str
        The agent's response as a string
    """
    with _create_agent(config) as solver:
        return solver.solve(query)
