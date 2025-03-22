from datetime import datetime
import argparse
import os
from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import Config
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.vector_database import VectorDatabase
from zk_chat.zettelkasten import Zettelkasten
from zk_chat.chroma_collections import ZkCollectionName


def reindex(config: Config, force_full: bool = False):
    db_dir = os.path.join(config.vault, ".zk_chat_db")
    chroma = ChromaGateway(db_dir=db_dir)
    zk = Zettelkasten(
        tokenizer_gateway=TokenizerGateway(),
        excerpts_db=VectorDatabase(
            chroma_gateway=chroma, 
            embeddings_gateway=EmbeddingsGateway(),
            collection_name=ZkCollectionName.EXCERPTS
        ),
        documents_db=VectorDatabase(
            chroma_gateway=chroma,
            embeddings_gateway=EmbeddingsGateway(),
            collection_name=ZkCollectionName.DOCUMENTS
        ),
        filesystem_gateway=MarkdownFilesystemGateway(config.vault))

    if force_full or config.last_indexed is None:
        print("Performing full reindex...")
        zk.reindex(excerpt_size=config.chunk_size, excerpt_overlap=config.chunk_overlap)
    else:
        print(f"Performing incremental reindex since {config.last_indexed}...")
        zk.update_index(since=config.last_indexed, excerpt_size=config.chunk_size, excerpt_overlap=config.chunk_overlap)

    config.last_indexed = datetime.now()
    config.save()


def main():
    parser = argparse.ArgumentParser(description='Reindex the Zettelkasten vault')
    parser.add_argument('--vault', required=True, help='Path to your Zettelkasten vault')
    parser.add_argument('--full', action='store_true', default=False, help='Force full reindex')
    args = parser.parse_args()

    # Ensure vault path exists
    if not os.path.exists(args.vault):
        print(f"Error: Vault path '{args.vault}' does not exist.")
        return

    # Get absolute path to vault
    vault_path = os.path.abspath(args.vault)

    config = Config.load_or_initialize(vault_path)
    reindex(config, force_full=args.full)


if __name__ == '__main__':
    main()
