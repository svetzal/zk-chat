import logging

logging.basicConfig(
    level=logging.WARN
)

from mojentic.llm import LLMBroker, ChatSession
from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.config import Config
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.rag.query import rag_query
from zk_chat.zettelkasten import Zettelkasten


def chat(config: Config):
    chroma = ChromaGateway()
    zk = Zettelkasten(root_path=config.vault, embeddings_gateway=EmbeddingsGateway(),
                      tokenizer_gateway=TokenizerGateway(),
                      document_db=chroma)
    llm = LLMBroker(config.model)

    chat_session = ChatSession(llm, system_prompt="You are a helpful research assistant.")

    while True:
        query = input("Query: ")
        if not query:
            break
        else:
            response = rag_query(chat_session, zk, query)
            print(response)


def main():
    config = Config.load_or_initialize()
    chat(config)


if __name__ == '__main__':
    main()
