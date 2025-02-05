from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from chroma_gateway import ChromaGateway
from settings import vault_root
from zettelkasten import Zettelkasten

chroma = ChromaGateway()
zk = Zettelkasten(root_path=vault_root, embeddings_gateway=EmbeddingsGateway(), tokenizer_gateway=TokenizerGateway(),
                  document_db=chroma)

zk.chunk_and_index(chunk_size=200, chunk_overlap=20)
