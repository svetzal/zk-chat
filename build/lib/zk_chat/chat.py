import logging

logging.basicConfig(
    level=logging.WARN
)

import argparse
import os

# Disable ChromaDB telemetry to avoid PostHog compatibility issues
os.environ['CHROMA_TELEMETRY'] = 'false'
from importlib.metadata import entry_points
from typing import List

from mojentic.llm.gateways import OllamaGateway, OpenAIGateway
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.cli import add_common_args, common_init, display_banner
from zk_chat.console_service import RichConsoleService
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.models import ZkDocument
from zk_chat.tools.analyze_image import AnalyzeImage
from zk_chat.tools.commit_changes import CommitChanges
from zk_chat.tools.git_gateway import GitGateway
from zk_chat.tools.list_zk_documents import ListZkDocuments
from zk_chat.tools.resolve_wikilink import ResolveWikiLink
from zk_chat.tools.retrieve_from_smart_memory import RetrieveFromSmartMemory
from zk_chat.tools.store_in_smart_memory import StoreInSmartMemory
from zk_chat.tools.uncommitted_changes import UncommittedChanges

from mojentic.llm.tools.date_resolver import ResolveDateTool

from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo
from zk_chat.tools.read_zk_document import ReadZkDocument
from zk_chat.tools.create_or_overwrite_zk_document import CreateOrOverwriteZkDocument
from zk_chat.tools.rename_zk_document import RenameZkDocument
from zk_chat.tools.delete_zk_document import DeleteZkDocument
from zk_chat.vector_database import VectorDatabase

from mojentic.llm import LLMBroker, ChatSession
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.config import Config, ModelGateway
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.zettelkasten import Zettelkasten
from zk_chat.services import ServiceRegistry, ServiceType, ServiceProvider


def chat(config: Config, unsafe: bool = False, use_git: bool = False, store_prompt: bool = False):
    console_service = RichConsoleService()

    # Create a single ChromaGateway instance to access multiple collections
    db_dir = os.path.join(config.vault, ".zk_chat_db")
    chroma_gateway = ChromaGateway(config.gateway, db_dir=db_dir)

    if config.gateway.value == ModelGateway.OLLAMA:
        gateway = OllamaGateway()
    elif config.gateway.value == ModelGateway.OPENAI:
        gateway = OpenAIGateway(os.environ.get("OPENAI_API_KEY"))
    else:
        raise ValueError(f"Invalid gateway: {config.gateway}")

    filesystem_gateway = MarkdownFilesystemGateway(config.vault)
    tokenizer_gateway = TokenizerGateway()

    zk = Zettelkasten(
        tokenizer_gateway=tokenizer_gateway,
        excerpts_db=VectorDatabase(
            chroma_gateway=chroma_gateway,
            gateway=gateway,
            collection_name=ZkCollectionName.EXCERPTS
        ),
        documents_db=VectorDatabase(
            chroma_gateway=chroma_gateway,
            gateway=gateway,
            collection_name=ZkCollectionName.DOCUMENTS
        ),
        filesystem_gateway=filesystem_gateway
    )

    llm = LLMBroker(config.model, gateway=gateway)

    # Create SmartMemory with the smart_memory collection
    smart_memory = SmartMemory(
        chroma_gateway=chroma_gateway,
        gateway=gateway
    )

    # Create and populate the service registry
    service_registry = ServiceRegistry()
    service_registry.register_service(ServiceType.CONFIG, config)
    service_registry.register_service(ServiceType.FILESYSTEM_GATEWAY, filesystem_gateway)
    service_registry.register_service(ServiceType.LLM_BROKER, llm)
    service_registry.register_service(ServiceType.ZETTELKASTEN, zk)
    service_registry.register_service(ServiceType.SMART_MEMORY, smart_memory)
    service_registry.register_service(ServiceType.CHROMA_GATEWAY, chroma_gateway)
    service_registry.register_service(ServiceType.MODEL_GATEWAY, gateway)
    service_registry.register_service(ServiceType.TOKENIZER_GATEWAY, tokenizer_gateway)

    tools: List[LLMTool] = [
        ResolveDateTool(),
        ReadZkDocument(zk, console_service),
        ListZkDocuments(zk, console_service),
        ResolveWikiLink(filesystem_gateway, console_service),
        FindExcerptsRelatedTo(zk, console_service),
        FindZkDocumentsRelatedTo(zk, console_service),
        StoreInSmartMemory(smart_memory, console_service),
        RetrieveFromSmartMemory(smart_memory, console_service)
    ]

    # Add AnalyzeImage tool only if a visual model is selected
    if config.visual_model:
        tools.append(AnalyzeImage(zk, LLMBroker(model=config.visual_model, gateway=gateway), console_service))

    if use_git:
        git_gateway = GitGateway(config.vault)
        service_registry.register_service(ServiceType.GIT_GATEWAY, git_gateway)
        tools.append(UncommittedChanges(config.vault, git_gateway))
        tools.append(CommitChanges(config.vault, llm, git_gateway))

    if unsafe:
        tools.append(CreateOrOverwriteZkDocument(zk, console_service))
        tools.append(RenameZkDocument(zk, console_service))
        tools.append(DeleteZkDocument(zk, console_service))

    _add_available_plugins(tools, service_registry)

    system_prompt_filename = "ZkSystemPrompt.md"
    default_system_prompt = """
You are a helpful research assistant, with access to one of the user's knowledge-bases (which the user may refer to as their vault, or zk, or Zettelkasten).
If you're not sure what the user is talking about, use your available tools try and find out.
If you don't find the information you need from the first tool you try, try the next best tool until you find what you need or exhaust your options..

About the Zettelkasten (zk):
All documents are in Markdown format, and links between them are in wikilink format (eg [[Title of Document]]).
Within the markdown:
- leave a blank line between headings, paragraphs, lists, code blocks, quotations, separators (---), and other block-level elements
- use # for headings, ## for subheadings, and so on
- don't repeat the document title as the first heading
- when nesting headings, their level should increase by one each time (#, ##, ###, etc.)
- only use `-` as the bullet marker for unordered lists, and 1. for ordered lists, renumber ordered lists if you insert or remove items
- use **bold** and *italic* for emphasis
- place blocks of code in code-fences, include a marker in the top fence for the type of code (language, json, xml, etc) eg "```python"
- when generating content use spaces (not tabs), and actual carriage returns (not `\\n` markers)
About organizing the Zettelkasten:
- An Atomic Idea is a document that contains a single idea, concept, or piece of information. It should be concise and focused, and consist of a title (the name of the document), a concise description of the core idea, a more elaborate explanation of the idea, a list of sources from which the idea was pulled (may be an external link), and a list of related ideas that are connected to the core idea (may be external links, but are likely to be wikilinks)
- Documents that refer to people should be in the form of `@Person Name` (eg under the wikilink `[[@Oscar Wilde]])
- There are several types of documents common in the zk - Atomic Ideas, editorial or blog content that expand on how Atomic Ideas relate, Maps of Content / index documents
- If the user uses a wikilink (eg [[Title of Document]], or [[@Person Name]]) to refer to a document in the zk, resolve the link to the actual document.
- If the user uses the phrase `MoC` that refers to a Map of Content, a document that indexes and links to other documents in order to assist a user in navigating the information in their vault
- The user may ask you to extract atomic ideas from a larger document, create one Atomic Idea document for each idea you find in the source document. Make sure to either transcribe the cited sources in the original document, and the original document itself.
- There must be only one reference to an Atomic Idea in the zk. If you find a duplicate, you should merge the two documents into one, and update the references to the merged document.
        """.strip()

    if zk.document_exists(system_prompt_filename):
        system_prompt = zk.read_document(system_prompt_filename).content
    else:
        system_prompt = default_system_prompt
        if store_prompt:
            zk.create_or_overwrite_document(
                ZkDocument(relative_path=system_prompt_filename, metadata={}, content=system_prompt))

    chat_session = ChatSession(
        llm,
        system_prompt=system_prompt,
        tools=tools
    )

    while True:
        query = console_service.input("[chat.user]Query:[/] ")
        if not query:
            console_service.print("[chat.system]Exiting...[/]")
            break
        else:
            # response = rag_query(chat_session, zk, query)
            response = chat_session.send(query)
            console_service.print(f"[chat.assistant]{response}[/]")


def _add_available_plugins(tools, service_registry: ServiceRegistry):
    """
    Load and add available plugins to the tools list.

    Plugins are discovered via entry points and initialized with a service provider
    that gives them access to all available services in the zk-chat runtime.
    """
    eps = entry_points()
    plugin_entr_points = eps.select(group="zk_rag_plugins")
    service_provider = ServiceProvider(service_registry)

    for ep in plugin_entr_points:
        logging.info(f"Adding Plugin {ep.name}")
        plugin_class = ep.load()
        # Prefer new-style constructor that accepts a ServiceProvider
        try:
            tools.append(plugin_class(service_provider))
            continue
        except TypeError as e:
            logging.warning(f"Plugin {ep.name} did not accept ServiceProvider (TypeError: {e}). Trying legacy constructors...")
            # Legacy fallback 1: constructor expects an LLM broker instance
            try:
                llm_broker = service_provider.get_llm_broker()
                tools.append(plugin_class(llm_broker))
                continue
            except Exception as e2:
                logging.warning(f"Plugin {ep.name} did not accept LLM broker (Exception: {e2}). Trying no-arg constructor...")
                # Legacy fallback 2: parameterless constructor
                try:
                    tools.append(plugin_class())
                    continue
                except Exception as e3:
                    logging.error(f"Failed to load plugin {ep.name}: {e3}")


def main() -> None:
    parser = argparse.ArgumentParser(description='Zettelkasten Chat')
    add_common_args(parser)
    parser.add_argument('--unsafe', action='store_true', help='Allow write operations in chat mode')
    parser.add_argument('--git', action='store_true', help='Enable git integration')
    parser.add_argument('--store-prompt', action='store_false', help='Store the system prompt to the vault',
                        dest='store_prompt', default=True)

    args = parser.parse_args()

    config = common_init(args)

    if args.git:
        git_gateway = GitGateway(config.vault)
        git_gateway.setup()

    display_banner(config, title="ZkChat", unsafe=args.unsafe, use_git=args.git, store_prompt=args.store_prompt)

    chat(config, unsafe=args.unsafe, use_git=args.git, store_prompt=args.store_prompt)


def chat_single_query(config: Config, query: str) -> str:
    """
    Execute a single query using the chat system and return the response.

    Args:
        config: Configuration object
        query: The query string to process

    Returns:
        The chat response as a string
    """
    # This is a simplified version for single queries
    # In a full implementation, you'd want to set up the full chat system
    # For now, we'll use the agent system as it's more capable
    from zk_chat.agent import agent_single_query
    return agent_single_query(config, query)


if __name__ == '__main__':
    main()
