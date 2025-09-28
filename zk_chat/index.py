from datetime import datetime
import argparse
import os

# Disable ChromaDB telemetry to avoid PostHog compatibility issues
os.environ['CHROMA_TELEMETRY'] = 'false'
from mojentic.llm.gateways import OllamaGateway, OpenAIGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import Config, ModelGateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.progress_tracker import IndexingProgressTracker
from zk_chat.vector_database import VectorDatabase
from zk_chat.zettelkasten import Zettelkasten
from zk_chat.chroma_collections import ZkCollectionName


def reindex(config: Config, force_full: bool = False):
    """Reindex the Zettelkasten vault with progress tracking."""
    db_dir = os.path.join(config.vault, ".zk_chat_db")

    chroma = ChromaGateway(config.gateway, db_dir=db_dir)

    # Create the appropriate gateway based on configuration
    if config.gateway == ModelGateway.OLLAMA:
        gateway = OllamaGateway()
    elif config.gateway == ModelGateway.OPENAI:
        gateway = OpenAIGateway(os.environ.get("OPENAI_API_KEY"))
    else:
        # Default to Ollama if not specified
        gateway = OllamaGateway()

    zk = Zettelkasten(
        tokenizer_gateway=TokenizerGateway(),
        excerpts_db=VectorDatabase(
            chroma_gateway=chroma,
            gateway=gateway,
            collection_name=ZkCollectionName.EXCERPTS
        ),
        documents_db=VectorDatabase(
            chroma_gateway=chroma,
            gateway=gateway,
            collection_name=ZkCollectionName.DOCUMENTS
        ),
        filesystem_gateway=MarkdownFilesystemGateway(config.vault))

    # Initialize progress tracker
    with IndexingProgressTracker() as progress:
        last_indexed = config.get_last_indexed()

        if force_full or last_indexed is None:
            # Full reindex
            progress.start_scanning()
            print("Performing full reindex...")

            # Create callback that will transition from scanning to processing
            files_processed = 0
            total_files = None

            def progress_callback(filename: str, processed_count: int, total_count: int):
                nonlocal files_processed, total_files

                if total_files is None:
                    # First callback - we now know the total
                    total_files = total_count
                    progress.finish_scanning(total_count)

                files_processed = processed_count
                progress.update_file_processing(filename, processed_count)

            zk.reindex(
                excerpt_size=config.chunk_size,
                excerpt_overlap=config.chunk_overlap,
                progress_callback=progress_callback
            )

        else:
            # Incremental reindex
            progress.start_scanning("Scanning for modified documents...")
            print(f"Performing incremental reindex since {last_indexed}...")

            files_processed = 0
            total_files = None

            def progress_callback(filename: str, processed_count: int, total_count: int):
                nonlocal files_processed, total_files

                if total_files is None:
                    # First callback - we now know the total
                    total_files = total_count
                    if total_count == 0:
                        progress.update_progress(description="No documents need updating")
                    else:
                        progress.finish_scanning(total_count)

                files_processed = processed_count
                if total_count > 0:
                    progress.update_file_processing(filename, processed_count)

            zk.update_index(
                since=last_indexed,
                excerpt_size=config.chunk_size,
                excerpt_overlap=config.chunk_overlap,
                progress_callback=progress_callback
            )

        # Show completion message
        if total_files == 0:
            print("\n✓ No documents needed updating")
        else:
            print(f"\n✓ Successfully processed {files_processed} document{'s' if files_processed != 1 else ''}")

    config.set_last_indexed(datetime.now())
    config.save()


def main():
    parser = argparse.ArgumentParser(description='Index the Zettelkasten vault')
    parser.add_argument('--vault', required=True, help='Path to your Zettelkasten vault')
    parser.add_argument('--full', action='store_true', default=False, help='Force full reindex')
    parser.add_argument('--gateway', choices=['ollama', 'openai'], default='ollama',
                        help='Set the model gateway to use (ollama or openai). OpenAI requires OPENAI_API_KEY environment variable')
    args = parser.parse_args()

    # Ensure vault path exists
    if not os.path.exists(args.vault):
        print(f"Error: Vault path '{args.vault}' does not exist.")
        return

    # Get absolute path to vault
    vault_path = os.path.abspath(args.vault)

    # Convert gateway string to ModelGateway enum
    gateway = ModelGateway(args.gateway)

    # Check if OpenAI API key is set when using OpenAI gateway
    if gateway == ModelGateway.OPENAI and not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set. Cannot use OpenAI gateway.")
        return

    config = Config.load(vault_path)
    if config:
        # Update gateway if different from config
        if gateway != config.gateway:
            config.gateway = gateway
            config.save()
    else:
        # Initialize new config with specified gateway
        config = Config.load_or_initialize(vault_path, gateway=gateway)

    reindex(config, force_full=args.full)


if __name__ == '__main__':
    main()
