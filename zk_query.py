import logging

logging.basicConfig(
    level=logging.WARN
)

from mojentic.llm import LLMBroker
from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway
from mojentic.llm.gateways.models import LLMMessage, MessageRole
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from chroma_gateway import ChromaGateway
from rag.query import rag_query
from settings import vault_root, ollama_model
from zettelkasten import Zettelkasten

chroma = ChromaGateway()
zk = Zettelkasten(root_path=vault_root, embeddings_gateway=EmbeddingsGateway(), tokenizer_gateway=TokenizerGateway(),
                  document_db=chroma)
llm = LLMBroker(ollama_model)

chat_history = [
    LLMMessage(role=MessageRole.System, content="You are a helpful research assistant."),
]
while True:
    query = input("Query: ")
    if not query:
        break
    else:
        response = rag_query(llm, zk, query, chat_history)
        print(response)
