from datetime import datetime
import argparse
from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import Config
from zk_chat.vector_database import VectorDatabase
from zk_chat.zettelkasten import Zettelkasten


def reindex(config: Config, force_full: bool = False):
    chroma = ChromaGateway()
    zk = Zettelkasten(root_path=config.vault,
                      tokenizer_gateway=TokenizerGateway(),
                      vector_db=VectorDatabase(chroma_gateway=chroma, embeddings_gateway=EmbeddingsGateway()))

    if force_full or config.last_indexed is None:
        print("Performing full reindex...")
        zk.split_and_index(excerpt_size=config.chunk_size, excerpt_overlap=config.chunk_overlap)
    else:
        print(f"Performing incremental reindex since {config.last_indexed}...")
        zk.incremental_split_and_index(since=config.last_indexed, excerpt_size=config.chunk_size, excerpt_overlap=config.chunk_overlap)
    
    config.last_indexed = datetime.now()
    config.save()


def main():
    parser = argparse.ArgumentParser(description='Reindex the Zettelkasten vault')
    parser.add_argument('--full', action='store_true', default=False, help='Force full reindex')
    args = parser.parse_args()

    config = Config.load_or_initialize()
    reindex(config, force_full=args.full)


if __name__ == '__main__':
    main()
