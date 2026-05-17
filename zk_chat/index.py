import argparse
import os
from datetime import datetime

import zk_chat.bootstrap  # noqa: F401  # Sets CHROMA_TELEMETRY and logging before chromadb imports
from zk_chat.config import Config, ModelGateway
from zk_chat.config_gateway import ConfigGateway
from zk_chat.console_gateway import ConsoleGateway
from zk_chat.index_resolution import determine_reindex_strategy
from zk_chat.model_selection import select_model
from zk_chat.progress_tracker import IndexingProgressTracker
from zk_chat.service_factory import build_service_registry_with_defaults
from zk_chat.services.index_service import IndexService
from zk_chat.services.service_provider import ServiceProvider
from zk_chat.vault_path import normalize_vault_path


def _full_reindex(
    config: Config,
    index_service: IndexService,
    progress: IndexingProgressTracker,
    console_gateway: ConsoleGateway,
) -> tuple[int, int]:
    progress.start_scanning()
    console_gateway.print("Performing full reindex...")
    files_processed = 0
    total_files: int | None = None

    def progress_callback(filename: str, processed_count: int, total_count: int) -> None:
        nonlocal files_processed, total_files
        if total_files is None:
            total_files = total_count
            progress.finish_scanning(total_count)
        files_processed = processed_count
        progress.update_file_processing(filename, processed_count)

    index_service.reindex_all(
        excerpt_size=config.chunk_size,
        excerpt_overlap=config.chunk_overlap,
        progress_callback=progress_callback,
    )
    return files_processed, total_files or 0


def _incremental_reindex(
    config: Config,
    index_service: IndexService,
    progress: IndexingProgressTracker,
    last_indexed: datetime,
    console_gateway: ConsoleGateway,
) -> tuple[int, int]:
    progress.start_scanning("Scanning for modified documents...")
    console_gateway.print(f"Performing incremental reindex since {last_indexed}...")
    files_processed = 0
    total_files: int | None = None

    def progress_callback(filename: str, processed_count: int, total_count: int) -> None:
        nonlocal files_processed, total_files
        if total_files is None:
            total_files = total_count
            if total_count == 0:
                progress.update_progress(description="No documents need updating")
            else:
                progress.finish_scanning(total_count)
        files_processed = processed_count
        if total_count > 0:
            progress.update_file_processing(filename, processed_count)

    index_service.update_index(
        since=last_indexed,
        excerpt_size=config.chunk_size,
        excerpt_overlap=config.chunk_overlap,
        progress_callback=progress_callback,
    )
    return files_processed, total_files or 0


def reindex(
    config: Config,
    config_gateway: ConfigGateway,
    force_full: bool = False,
    *,
    console_gateway: ConsoleGateway,
    _provider_factory=None,
    _progress_factory=None,
) -> None:
    """Reindex the Zettelkasten vault with progress tracking."""
    registry = build_service_registry_with_defaults(config)
    provider = _provider_factory(registry) if _provider_factory else ServiceProvider(registry)
    index_service = provider.get_index_service()

    decision = determine_reindex_strategy(force_full=force_full, last_indexed=config.get_last_indexed())

    progress_cls = _progress_factory or IndexingProgressTracker
    with progress_cls() as progress:
        if decision.strategy == "full":
            files_processed, total_files = _full_reindex(config, index_service, progress, console_gateway)
        else:
            files_processed, total_files = _incremental_reindex(
                config, index_service, progress, decision.last_indexed, console_gateway
            )

        if total_files == 0:
            console_gateway.print("\n✓ No documents needed updating")
        else:
            console_gateway.print(
                f"\n✓ Successfully processed {files_processed} document{'s' if files_processed != 1 else ''}"
            )

    config.set_last_indexed(datetime.now())
    config_gateway.save(config)


def main(config_gateway: ConfigGateway, console_gateway: ConsoleGateway) -> None:
    parser = argparse.ArgumentParser(description="Index the Zettelkasten vault")
    parser.add_argument("--vault", required=True, help="Path to your Zettelkasten vault")
    parser.add_argument("--full", action="store_true", default=False, help="Force full reindex")
    parser.add_argument(
        "--gateway",
        choices=["ollama", "openai"],
        default="ollama",
        help="Set the model gateway to use (ollama or openai). OpenAI requires OPENAI_API_KEY environment variable",
    )
    args = parser.parse_args()

    if not os.path.exists(args.vault):
        console_gateway.print(f"Error: Vault path '{args.vault}' does not exist.")
        return

    vault_path = normalize_vault_path(args.vault)

    gateway = ModelGateway(args.gateway)

    if gateway == ModelGateway.OPENAI and not os.environ.get("OPENAI_API_KEY"):
        console_gateway.print("Error: OPENAI_API_KEY environment variable is not set. Cannot use OpenAI gateway.")
        return

    config = config_gateway.load(vault_path)
    if config:
        if gateway != config.gateway:
            config.gateway = gateway
            config_gateway.save(config)
    else:
        console_gateway.print("Please select a model for chat:")
        model = select_model(gateway, console_gateway=console_gateway)
        config = Config(vault=vault_path, model=model, gateway=gateway)
        config_gateway.save(config)

    reindex(config, config_gateway, force_full=args.full, console_gateway=console_gateway)


if __name__ == "__main__":
    from zk_chat.gateway_defaults import create_default_config_gateway

    main(config_gateway=create_default_config_gateway(), console_gateway=ConsoleGateway())
