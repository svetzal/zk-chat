import logging

logging.basicConfig(
    level=logging.WARN
)

from mojentic.llm import LLMBroker, ChatSession
from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.config import load_or_initialize_config
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.rag.query import rag_query
from zk_chat.zettelkasten import Zettelkasten


def chat(vault, model):
    chroma = ChromaGateway()
    zk = Zettelkasten(root_path=vault, embeddings_gateway=EmbeddingsGateway(), tokenizer_gateway=TokenizerGateway(),
                      document_db=chroma)
    llm = LLMBroker(model)

    chat_session = ChatSession(llm, system_prompt="You are a helpful research assistant.")

    while True:
        query = input("Query: ")
        if not query:
            break
        else:
            response = rag_query(chat_session, zk, query)
            print(response)


def main():
    print("Running zk_chat main function")
    vault, model = load_or_initialize_config()
    chat(vault, model)


if __name__ == '__main__':
    main()
