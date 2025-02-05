from mojentic.llm import LLMBroker
from mojentic.llm.gateways.models import LLMMessage, MessageRole

from chroma_gateway import ChromaGateway
from rag.query import rag_query
from settings import vault_root, ollama_model
from zettelkasten import Zettelkasten

chroma = ChromaGateway()
zk = Zettelkasten(vault_root, chroma)
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
