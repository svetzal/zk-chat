from mojentic.llm import LLMBroker

from chroma_gateway import ChromaGateway
from settings import vault_root, ollama_model
from zettelkasten import Zettelkasten

chroma = ChromaGateway()
zk = Zettelkasten(vault_root, chroma)
llm = LLMBroker(ollama_model)

zk.chunk_and_index(chunk_size=200, chunk_overlap=20)
