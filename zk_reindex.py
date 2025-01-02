from chroma_gateway import ChromaGateway
from llm_gateway import LLMGateway
from settings import vault_root, ollama_model
from zettelkasten import Zettelkasten

chroma = ChromaGateway()
zk = Zettelkasten(vault_root, chroma)
llm = LLMGateway(ollama_model)

zk.chunk_and_index(chunk_size=200, chunk_overlap=20)
