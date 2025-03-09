import logging
from importlib.metadata import entry_points

from zk_chat.filesystem_gateway import FilesystemGateway
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.tools.retrieve_from_smart_memory import RetrieveFromSmartMemory
from zk_chat.tools.store_in_smart_memory import StoreInSmartMemory

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
    zk_chroma = ChromaGateway()
    zk = Zettelkasten(tokenizer_gateway=TokenizerGateway(),
                      vector_db=VectorDatabase(chroma_gateway=zk_chroma, embeddings_gateway=EmbeddingsGateway()),
                      filesystem_gateway=FilesystemGateway(config.vault))

    llm = LLMBroker(config.model)

    sm_chroma = ChromaGateway(partition_name="smart_memory")
    smart_memory = SmartMemory(chroma_gateway=sm_chroma, embeddings_gateway=EmbeddingsGateway())

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

    _add_available_plugins(tools, config)

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
    config = Config.load_or_initialize()
    chat(config)


if __name__ == '__main__':
    main()
