import logging

logging.basicConfig(
    level=logging.WARN
)

import argparse
import os

# Disable ChromaDB telemetry to avoid PostHog compatibility issues
os.environ['CHROMA_TELEMETRY'] = 'false'
from pathlib import Path
from typing import List

from mojentic.llm import LLMBroker
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway
from mojentic.llm.tools.date_resolver import ResolveDateTool
from mojentic.llm.tools.current_datetime import CurrentDateTimeTool
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.cli import add_common_args, common_init, display_banner
from zk_chat.config import Config, ModelGateway
from zk_chat.iterative_problem_solving_agent import IterativeProblemSolvingAgent
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.tools.analyze_image import AnalyzeImage
from zk_chat.tools.commit_changes import CommitChanges
from zk_chat.tools.create_or_overwrite_zk_document import CreateOrOverwriteZkDocument
from zk_chat.tools.delete_zk_document import DeleteZkDocument
from zk_chat.tools.extract_wikilinks_from_document import ExtractWikilinksFromDocument
from zk_chat.tools.find_backlinks import FindBacklinks
from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo
from zk_chat.tools.find_forward_links import FindForwardLinks
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo
from zk_chat.tools.git_gateway import GitGateway
from zk_chat.tools.list_zk_documents import ListZkDocuments
from zk_chat.tools.read_zk_document import ReadZkDocument
from zk_chat.tools.rename_zk_document import RenameZkDocument
from zk_chat.tools.resolve_wikilink import ResolveWikiLink
from zk_chat.tools.retrieve_from_smart_memory import RetrieveFromSmartMemory
from zk_chat.tools.store_in_smart_memory import StoreInSmartMemory
from zk_chat.tools.uncommitted_changes import UncommittedChanges
from zk_chat.vector_database import VectorDatabase
from zk_chat.zettelkasten import Zettelkasten

from mojentic.llm.gateways import OllamaGateway
from mojentic.llm.gateways import OpenAIGateway
from zk_chat.chroma_gateway import ChromaGateway


def agent(config: Config):
    db_dir = os.path.join(config.vault, ".zk_chat_db")
    chroma_gateway = ChromaGateway(config.gateway, db_dir=db_dir)

    if config.gateway.value == ModelGateway.OLLAMA:
        gateway = OllamaGateway()
    elif config.gateway.value == ModelGateway.OPENAI:
        gateway = OpenAIGateway(os.environ.get("OPENAI_API_KEY"))
    else:
        raise ValueError(f"Invalid gateway: {config.gateway}")

    filesystem_gateway = MarkdownFilesystemGateway(config.vault)
    zk = Zettelkasten(
        tokenizer_gateway=TokenizerGateway(),
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

    smart_memory = SmartMemory(
        chroma_gateway=chroma_gateway,
        gateway=gateway
    )

    git_gateway = GitGateway(config.vault)

    tools: List[LLMTool] = [
        # Real world context
        CurrentDateTimeTool(),
        ResolveDateTool(),

        # Document tools
        ReadZkDocument(zk),
        ListZkDocuments(zk),
        ResolveWikiLink(filesystem_gateway),
        FindExcerptsRelatedTo(zk),
        FindZkDocumentsRelatedTo(zk),
        CreateOrOverwriteZkDocument(zk),
        RenameZkDocument(zk),
        DeleteZkDocument(zk),

        # Graph traversal tools
        ExtractWikilinksFromDocument(zk),
        FindBacklinks(zk),
        FindForwardLinks(zk),

        # Memory tools
        StoreInSmartMemory(smart_memory),
        RetrieveFromSmartMemory(smart_memory),

        # Visual tools
        AnalyzeImage(zk, LLMBroker(model=config.visual_model, gateway=gateway)),

        # Git tools
        UncommittedChanges(config.vault, git_gateway),
        CommitChanges(config.vault, llm, git_gateway)
    ]

    agent_prompt_path = Path(__file__).parent / "agent_prompt.txt"
    with open(agent_prompt_path, "r") as f:
        agent_prompt = f.read()

    solver = IterativeProblemSolvingAgent(llm=llm, available_tools=tools, system_prompt=agent_prompt)

    while True:

        query = input("Agent request: ")
        if not query:
            break
        else:
            response = solver.solve(query)
            print(response)


def main():
    parser = argparse.ArgumentParser(description='Zettelkasten Agent')
    add_common_args(parser)

    args = parser.parse_args()

    config = common_init(args)

    if not config:  # common_init returns None for certain operations like --list-bookmarks
        return

    git_gateway = GitGateway(config.vault)
    git_gateway.setup()

    display_banner(config, title="ZkAgent", unsafe=True, use_git=True, store_prompt=False)

    agent(config)


def agent_single_query(config: Config, query: str) -> str:
    """
    Execute a single query using the agent and return the response.

    Args:
        config: Configuration object
        query: The query string to process

    Returns:
        The agent's response as a string
    """
    db_dir = os.path.join(config.vault, ".zk_chat_db")
    chroma_gateway = ChromaGateway(config.gateway, db_dir=db_dir)

    if config.gateway.value == ModelGateway.OLLAMA:
        gateway = OllamaGateway()
    elif config.gateway.value == ModelGateway.OPENAI:
        gateway = OpenAIGateway(os.environ.get("OPENAI_API_KEY"))
    else:
        raise ValueError(f"Invalid gateway: {config.gateway}")

    filesystem_gateway = MarkdownFilesystemGateway(config.vault)
    zk = Zettelkasten(
        tokenizer_gateway=TokenizerGateway(),
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
    smart_memory = SmartMemory(chroma_gateway=chroma_gateway, gateway=gateway)
    git_gateway = GitGateway(config.vault)

    tools: List[LLMTool] = [
        # Real world context
        CurrentDateTimeTool(),
        ResolveDateTool(),

        # Document tools
        ReadZkDocument(zk),
        ListZkDocuments(zk),
        ResolveWikiLink(filesystem_gateway),
        FindExcerptsRelatedTo(zk),
        FindZkDocumentsRelatedTo(zk),
        CreateOrOverwriteZkDocument(zk),
        RenameZkDocument(zk),
        DeleteZkDocument(zk),

        # Graph traversal tools
        ExtractWikilinksFromDocument(zk),
        FindBacklinks(zk),
        FindForwardLinks(zk),

        # Memory tools
        StoreInSmartMemory(smart_memory),
        RetrieveFromSmartMemory(smart_memory),

        # Visual tools
        AnalyzeImage(zk, LLMBroker(model=config.visual_model, gateway=gateway)),

        # Git tools
        UncommittedChanges(config.vault, git_gateway),
        CommitChanges(config.vault, llm, git_gateway)
    ]

    agent_prompt_path = Path(__file__).parent / "agent_prompt.txt"
    with open(agent_prompt_path, "r") as f:
        agent_prompt = f.read()

    solver = IterativeProblemSolvingAgent(llm=llm, available_tools=tools, system_prompt=agent_prompt)

    return solver.solve(query)


if __name__ == '__main__':
    main()
