import logging
import os
import argparse
from importlib.metadata import entry_points

from zk_chat.filesystem_gateway import FilesystemGateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.tools.retrieve_from_smart_memory import RetrieveFromSmartMemory
from zk_chat.tools.store_in_smart_memory import StoreInSmartMemory
from zk_chat.chroma_collections import ZkCollectionName

logging.basicConfig(
    level=logging.WARN
)

from mojentic.llm.tools.date_resolver import ResolveDateTool

from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo
from zk_chat.tools.read_zk_document import ReadZkDocument
from zk_chat.tools.create_or_overwrite_zk_document import CreateOrOverwriteZkDocument
from zk_chat.vector_database import VectorDatabase

from mojentic.llm import LLMBroker, ChatSession
from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.config import Config
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.zettelkasten import Zettelkasten


def chat(config: Config, unsafe: bool = False):
    # Create a single ChromaGateway instance to access multiple collections
    db_dir = os.path.join(config.vault, ".zk_chat_db")
    chroma_gateway = ChromaGateway(db_dir=db_dir)

    # Create Zettelkasten with the excerpts collection
    zk = Zettelkasten(
        tokenizer_gateway=TokenizerGateway(),
        vector_db=VectorDatabase(
            chroma_gateway=chroma_gateway, 
            embeddings_gateway=EmbeddingsGateway(),
            collection_name=ZkCollectionName.EXCERPTS
        ),
        filesystem_gateway=MarkdownFilesystemGateway(config.vault)
    )

    llm = LLMBroker(config.model)

    # Create SmartMemory with the smart_memory collection
    smart_memory = SmartMemory(
        chroma_gateway=chroma_gateway, 
        embeddings_gateway=EmbeddingsGateway()
    )

    tools = [
        ResolveDateTool(),
        ReadZkDocument(zk),
        FindExcerptsRelatedTo(zk),
        FindZkDocumentsRelatedTo(zk),
        StoreInSmartMemory(smart_memory),
        RetrieveFromSmartMemory(smart_memory),
    ]

    if unsafe:
        tools.append(CreateOrOverwriteZkDocument(zk))

    _add_available_plugins(tools, config, llm)

    chat_session = ChatSession(
        llm,
        system_prompt="You are a helpful research assistant.",
        tools=tools
    )

    while True:
        query = input("Query: ")
        if not query:
            break
        else:
            # response = rag_query(chat_session, zk, query)
            response = chat_session.send(query)
            print(response)


def _add_available_plugins(tools, config: Config, llm: LLMBroker):
    eps = entry_points()
    plugin_entr_points = eps.select(group="zk_rag_plugins")
    for ep in plugin_entr_points:
        logging.info(f"Adding Plugin {ep.name}")
        plugin_class = ep.load()
        tools.append(plugin_class(vault=config.vault, llm=llm))


def main():
    parser = argparse.ArgumentParser(description='Chat with your Zettelkasten vault')
    parser.add_argument('--vault', required=True, help='Path to your Zettelkasten vault')
    parser.add_argument('--unsafe', action='store_true', help='Allow write operations in chat mode')
    args = parser.parse_args()

    # Ensure vault path exists
    if not os.path.exists(args.vault):
        print(f"Error: Vault path '{args.vault}' does not exist.")
        return

    # Get absolute path to vault
    vault_path = os.path.abspath(args.vault)

    config = Config.load_or_initialize(vault_path)
    chat(config, unsafe=args.unsafe)


if __name__ == '__main__':
    main()
