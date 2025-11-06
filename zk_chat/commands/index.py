# ruff: noqa: E402  # Configure logging/env before imports to reduce noisy logs and disable telemetry
"""
Index subcommand for zk-chat.

Manages the search index for your Zettelkasten.
"""
import logging
import os

# Set log levels early to prevent chatty output
logging.basicConfig(level=logging.WARN)

# Disable ChromaDB telemetry to avoid PostHog compatibility issues
os.environ['CHROMA_TELEMETRY'] = 'false'

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from zk_chat.cli import common_init_typer
from zk_chat.config import Config
from zk_chat.global_config import GlobalConfig

index_app = typer.Typer(
    name="index",
    help="🔍 Manage your Zettelkasten search index",
    rich_markup_mode="rich"
)

console = Console()


@index_app.command()
def update(
        vault: Annotated[Path | None, typer.Option("--vault", "-v",
                                                   help="Path to your Zettelkasten vault")] = None,
        full: Annotated[bool, typer.Option("--full",
                                           help="Force full rebuild (slower but comprehensive)")]
        = False,
        gateway: Annotated[str | None, typer.Option("--gateway", "-g",
                                                    help="Model gateway (ollama/openai)")] = None,
        model: Annotated[str | None, typer.Option("--model", "-m",
                                                  help="Model for generating embeddings")] = None,
):
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

    class Args:
        def __init__(self):
            self.vault = str(vault) if vault else None
            self.save = False
            self.gateway = gateway
            self.model = model
            self.visual_model = None
            self.reindex = True  # This is an index command, always reindex
            self.full = full
            self.unsafe = False
            self.git = False
            self.store_prompt = True
            self.reset_memory = False
            self.remove_bookmark = None
            self.list_bookmarks = False

    args = Args()
    config = common_init_typer(args)

    if not config:
        return

    # The reindexing will happen in common_init_typer since args.reindex = True
    console.print("\n[green]✅ Index update completed![/]")
    console.print("[dim]Your Zettelkasten is ready for fast searching.[/]")




def _resolve_vault_status(vault: Path | None) -> str:
    import os as _os
    if vault:
        vault_path = str(vault.resolve())
    else:
        global_config = GlobalConfig.load()
        vault_path = global_config.get_last_opened_bookmark_path()
        if not vault_path:
            console.print("[red]❌ Error:[/] No vault specified and no bookmarks found.")
            console.print("[yellow]Use:[/] [cyan]zk-chat index status --vault /path/to/vault[/]")
            raise typer.Exit(1)
    if not _os.path.exists(vault_path):
        console.print(f"[red]❌ Error:[/] Vault path '{vault_path}' does not exist.")
        raise typer.Exit(1)
    return vault_path


def _load_config_status(vault_path: str):
    config = Config.load(vault_path)
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
    last_indexed = config.get_last_indexed()
    if last_indexed:
        console.print(f"\n[bold]Last Indexed:[/] {last_indexed.strftime('%Y-%m-%d %H:%M:%S')}")
        time_diff = _dt.now() - last_indexed
        if time_diff.days > 0:
            console.print(f"[yellow]⚠️  {time_diff.days} day(s) ago - consider updating[/]")
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            console.print(f"[green]✅ {hours} hour(s) ago - up to date[/]")
        else:
            console.print("[green]✅ Recently updated[/]")
    else:
        console.print("\n[red]❌ Never indexed[/]")


def _print_db_info(vault_path: str) -> None:
    import os as _os
    db_dir = _os.path.join(vault_path, ".zk_chat_db")
    if _os.path.exists(db_dir):
        total_size = 0
        file_count = 0
        for dirpath, _dirnames, filenames in _os.walk(db_dir):
            for filename in filenames:
                filepath = _os.path.join(dirpath, filename)
                total_size += _os.path.getsize(filepath)
                file_count += 1
        if total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        elif total_size < 1024 * 1024 * 1024:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{total_size / (1024 * 1024 * 1024):.1f} GB"
        console.print("\n[bold]Index Database:[/]")
        console.print(f"  • Location: {db_dir}")
        console.print(f"  • Size: {size_str}")
        console.print(f"  • Files: {file_count}")
    else:
        console.print("\n[yellow]⚠️  No index database found[/]")


def _count_markdown_files(vault_path: str) -> int:
    import os as _os
    count = 0
    for root, _dirs, files in _os.walk(vault_path):
        if '.zk_chat_db' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                count += 1
    return count


def _print_health(last_indexed, markdown_count: int, vault_path: str) -> None:
    console.print("\n[bold]Vault Statistics:[/]")
    console.print(f"  • Markdown files: {markdown_count}")
    if last_indexed and markdown_count > 0:
        console.print("\n[green]✅ Index appears healthy[/]")
    elif markdown_count == 0:
        console.print("\n[yellow]⚠️  No markdown files found in vault[/]")
    else:
        console.print("\n[red]❌ Index needs updating[/]")
        console.print("[dim]Run: [cyan]zk-chat index update[/dim]")
        console.print(f"[yellow]Run:[/] [cyan]zk-chat index update --vault {vault_path}[/]")


@index_app.command()
def status(
        vault: Annotated[Path | None, typer.Option("--vault", "-v", help="Path to your Zettelkasten vault")] = None,
):
    """Show the current status of your Zettelkasten index."""
    vault_path = _resolve_vault_status(vault)
    config = _load_config_status(vault_path)
    console.print(f"[bold cyan]Index Status[/] - {vault_path}")
    _print_basic_config(config)
    _print_last_indexed(config)
    _print_db_info(vault_path)
    markdown_count = _count_markdown_files(vault_path)
    last_indexed = config.get_last_indexed()
    _print_health(last_indexed, markdown_count, vault_path)


# Default command
@index_app.callback()
def index_default(ctx: typer.Context):
    """
    Manage your Zettelkasten search index.

    The index enables fast semantic search across your notes.
    Use [cyan]update[/] to refresh it and [cyan]status[/] to check its health.
    """
    if ctx.invoked_subcommand is None:
        # Show help by default
        console.print(ctx.get_help())
        console.print(
            "\n[yellow]💡 Tip:[/] Use [cyan]zk-chat index --help[/] to see available commands.")
        console.print("Most common: [cyan]zk-chat index update[/] or [cyan]zk-chat index status[/]")
