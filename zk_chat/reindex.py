from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import load_or_initialize_config, Config
from zk_chat.zettelkasten import Zettelkasten


def reindex(config: Config):
    chroma = ChromaGateway()
    zk = Zettelkasten(root_path=config.vault, embeddings_gateway=EmbeddingsGateway(), tokenizer_gateway=TokenizerGateway(),
                      document_db=chroma)

    zk.chunk_and_index(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)


def main():
    config = load_or_initialize_config()
    reindex(config)


if __name__ == '__main__':
    main()
