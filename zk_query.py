from chroma_gateway import ChromaGateway
from llm_gateway import LLMGateway
from rag.query import rag_query
from settings import vault_root, ollama_model
from zettelkasten import Zettelkasten

chroma = ChromaGateway()
zk = Zettelkasten(vault_root, chroma)
llm = LLMGateway(ollama_model)

while True:
    query = input("Query: ")
    if not query:
        break
    else:
        response = rag_query(llm, zk, query)
        print(response)
