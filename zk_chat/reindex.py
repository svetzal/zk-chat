from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import load_or_initialize_config
from zk_chat.zettelkasten import Zettelkasten


def reindex(vault):
    chroma = ChromaGateway()
    zk = Zettelkasten(root_path=vault, embeddings_gateway=EmbeddingsGateway(), tokenizer_gateway=TokenizerGateway(),
                      document_db=chroma)

    zk.chunk_and_index(chunk_size=200, chunk_overlap=20)


def main():
    print("Running zk_reindex main function")
    vault, model = load_or_initialize_config()
    reindex(vault)


if __name__ == '__main__':
    main()
