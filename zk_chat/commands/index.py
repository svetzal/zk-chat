"""
Index subcommand for zk-chat.

Manages the search index for your Zettelkasten.
"""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

import zk_chat.bootstrap  # noqa: F401  # Sets CHROMA_TELEMETRY and logging before chromadb imports
from zk_chat.cli import common_init
from zk_chat.config import Config
from zk_chat.config_gateway import ConfigGateway
from zk_chat.gateway_defaults import (
    create_default_config_gateway,
    create_default_filesystem_gateway,
    create_default_global_config_gateway,
)
from zk_chat.init_options import InitOptions
from zk_chat.vault_resolution import VaultResolutionError, resolve_vault_path

index_app = typer.Typer(name="index", help="🔍 Manage your Zettelkasten search index", rich_markup_mode="rich")

console = Console()


@index_app.command()
def update(
    vault: Annotated[Path | None, typer.Option("--vault", "-v", help="Path to your Zettelkasten vault")] = None,
    full: Annotated[bool, typer.Option("--full", help="Force full rebuild (slower but comprehensive)")] = False,
    gateway: Annotated[str | None, typer.Option("--gateway", "-g", help="Model gateway (ollama/openai)")] = None,
    model: Annotated[str | None, typer.Option("--model", "-m", help="Model for generating embeddings")] = None,
) -> None:
    """
    Update the search index for your Zettelkasten.

    [bold]Index Types:[/]

    • [green]Incremental[/] (default): Only processes new/modified files
    • [green]Full[/] (--full): Rebuilds entire index from scratch

    [bold]Examples:[/]

    • [cyan]zk-chat index update[/] - Quick incremental update
    • [cyan]zk-chat index update --full[/] - Complete rebuild
    • [cyan]zk-chat index update --vault ~/notes[/] - Update specific vault

    [bold yellow]💡 Tip:[/] Incremental update is fast and happens automatically on startup.
    Use --full after major changes or for troubleshooting.
    """

    options = InitOptions(
        vault=str(vault) if vault else None,
        gateway=gateway,
        model=model,
        reindex=True,
        full=full,
    )
    config = common_init(options, create_default_global_config_gateway(), create_default_config_gateway())

    if not config:
        return

    # The reindexing happens in common_init since options.reindex = True
    console.print("\n[green]✅ Index update completed![/]")
    console.print("[dim]Your Zettelkasten is ready for fast searching.[/]")


def _load_config_status(vault_path: str, config_gateway: ConfigGateway) -> Config:
    config = config_gateway.load(vault_path)
    if not config:
        console.print("[yellow]⚠️  Warning:[/] No zk-chat configuration found in vault.")
        console.print("[dim]Run [cyan]zk-chat interactive --vault {vault_path}[/dim] to initialize.")
        raise typer.Exit(1)
    return config


def _print_basic_config(config) -> None:
    console.print("=" * 60)
    console.print(f"[bold]Gateway:[/] {config.gateway.value}")
    console.print(f"[bold]Model:[/] {config.model}")
    if config.visual_model:
        console.print(f"[bold]Visual Model:[/] {config.visual_model}")
    console.print("\n[bold]Chunk Settings:[/]")
    console.print(f"  • Size: {config.chunk_size} tokens")
    console.print(f"  • Overlap: {config.chunk_overlap} tokens")


def _print_last_indexed(config) -> None:
    from datetime import datetime as _dt

    from zk_chat.formatting import categorize_index_age

    last_indexed = config.get_last_indexed()
    if last_indexed:
        console.print(f"\n[bold]Last Indexed:[/] {last_indexed.strftime('%Y-%m-%d %H:%M:%S')}")
        age = categorize_index_age(last_indexed, _dt.now())
        if age.category == "stale":
            console.print(f"[yellow]⚠️  {age.description}[/]")
        else:
            console.print(f"[green]✅ {age.description}[/]")
    else:
        console.print("\n[red]❌ Never indexed[/]")


def _print_db_info(vault_path: str, db_info) -> None:
    from zk_chat.formatting import format_file_size

    if db_info:
        console.print("\n[bold]Index Database:[/]")
        console.print(f"  • Location: {db_info.location}")
        console.print(f"  • Size: {format_file_size(db_info.total_size)}")
        console.print(f"  • Files: {db_info.file_count}")
    else:
        console.print("\n[yellow]⚠️  No index database found[/]")


def _print_health(last_indexed, markdown_count: int, vault_path: str) -> None:
    from zk_chat.formatting import assess_vault_health

    console.print("\n[bold]Vault Statistics:[/]")
    console.print(f"  • Markdown files: {markdown_count}")
    health = assess_vault_health(last_indexed, markdown_count)
    if health.status == "healthy":
        console.print("\n[green]✅ Index appears healthy[/]")
    elif health.status == "no_files":
        console.print("\n[yellow]⚠️  No markdown files found in vault[/]")
    else:
        console.print("\n[red]❌ Index needs updating[/]")
        console.print("[dim]Run: [cyan]zk-chat index update[/dim]")
        console.print(f"[yellow]Run:[/] [cyan]zk-chat index update --vault {vault_path}[/]")


@index_app.command()
def status(
    vault: Annotated[Path | None, typer.Option("--vault", "-v", help="Path to your Zettelkasten vault")] = None,
) -> None:
    """Show the current status of your Zettelkasten index."""
    try:
        vault_path = resolve_vault_path(vault, create_default_global_config_gateway())
    except VaultResolutionError as e:
        console.print(f"[red]❌ Error:[/] {e}")
        console.print("[yellow]Use:[/] [cyan]zk-chat index status --vault /path/to/vault[/]")
        raise typer.Exit(1) from e

    from zk_chat.services.vault_status_service import VaultStatusService

    config = _load_config_status(vault_path, create_default_config_gateway())
    filesystem_gateway = create_default_filesystem_gateway(vault_path)
    vault_status = VaultStatusService(filesystem_gateway)
    console.print(f"[bold cyan]Index Status[/] - {vault_path}")
    _print_basic_config(config)
    _print_last_indexed(config)
    _print_db_info(vault_path, vault_status.get_db_info(vault_path))
    last_indexed = config.get_last_indexed()
    _print_health(last_indexed, vault_status.count_markdown_files(), vault_path)


@index_app.callback()
def index_default(ctx: typer.Context) -> None:
    """
    Manage your Zettelkasten search index.

    The index enables fast semantic search across your notes.
    Use [cyan]update[/] to refresh it and [cyan]status[/] to check its health.
    """
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        console.print("\n[yellow]💡 Tip:[/] Use [cyan]zk-chat index --help[/] to see available commands.")
        console.print("Most common: [cyan]zk-chat index update[/] or [cyan]zk-chat index status[/]")
