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

import typer
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated
from rich.console import Console

from zk_chat.cli import common_init_typer

index_app = typer.Typer(
    name="index",
    help="🔍 Manage your Zettelkasten search index",
    rich_markup_mode="rich"
)

console = Console()


@index_app.command()
def rebuild(
    vault: Annotated[Optional[Path], typer.Option("--vault", "-v", help="Path to your Zettelkasten vault")] = None,
    full: Annotated[bool, typer.Option("--full", help="Force full rebuild (slower but comprehensive)")] = False,
    gateway: Annotated[Optional[str], typer.Option("--gateway", "-g", help="Model gateway (ollama/openai)")] = None,
    model: Annotated[Optional[str], typer.Option("--model", "-m", help="Model for generating embeddings")] = None,
):
    """
    Rebuild the search index for your Zettelkasten.

    [bold]Index Types:[/]

    • [green]Incremental[/] (default): Only processes new/modified files
    • [green]Full[/] (--full): Rebuilds entire index from scratch

    [bold]Examples:[/]

    • [cyan]zk-chat index rebuild[/] - Quick incremental update
    • [cyan]zk-chat index rebuild --full[/] - Complete rebuild
    • [cyan]zk-chat index rebuild --vault ~/notes[/] - Rebuild specific vault

    [bold yellow]💡 Tip:[/] Use incremental rebuild for regular maintenance,
    full rebuild after major changes or troubleshooting.
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
    console.print("\n[green]✅ Index rebuild completed![/]")
    console.print("[dim]Your Zettelkasten is ready for fast searching.[/]")


@index_app.command()
def status(
    vault: Annotated[Optional[Path], typer.Option("--vault", "-v", help="Path to your Zettelkasten vault")] = None,
):
    """
    Show the current status of your Zettelkasten index.

    [bold]Information displayed:[/]

    • Last index update time
    • Number of indexed documents
    • Index size and statistics
    • Configuration details

    [bold]Examples:[/]

    • [cyan]zk-chat index status[/] - Show status for bookmarked vault
    • [cyan]zk-chat index status --vault ~/notes[/] - Show status for specific vault
    """
    from zk_chat.config import Config
    from zk_chat.global_config import GlobalConfig
    import os
    from datetime import datetime

    # Determine vault path
    if vault:
        vault_path = str(vault.resolve())
    else:
        global_config = GlobalConfig.load()
        vault_path = global_config.get_last_opened_bookmark_path()
        if not vault_path:
            console.print("[red]❌ Error:[/] No vault specified and no bookmarks found.")
            console.print("[yellow]Use:[/] [cyan]zk-chat index status --vault /path/to/vault[/]")
            raise typer.Exit(1)

    if not os.path.exists(vault_path):
        console.print(f"[red]❌ Error:[/] Vault path '{vault_path}' does not exist.")
        raise typer.Exit(1)

    # Load config
    config = Config.load(vault_path)
    if not config:
        console.print("[yellow]⚠️  Warning:[/] No zk-chat configuration found in vault.")
        console.print("[dim]Run [cyan]zk-chat interactive --vault {vault_path}[/dim] to initialize.")
        raise typer.Exit(1)

    # Display status information
    console.print(f"[bold cyan]Index Status[/] - {vault_path}")
    console.print("=" * 60)

    # Basic configuration
    console.print(f"[bold]Gateway:[/] {config.gateway.value}")
    console.print(f"[bold]Model:[/] {config.model}")
    if config.visual_model:
        console.print(f"[bold]Visual Model:[/] {config.visual_model}")

    console.print(f"\n[bold]Chunk Settings:[/]")
    console.print(f"  • Size: {config.chunk_size} tokens")
    console.print(f"  • Overlap: {config.chunk_overlap} tokens")

    # Index information
    last_indexed = config.get_last_indexed()
    if last_indexed:
        console.print(f"\n[bold]Last Indexed:[/] {last_indexed.strftime('%Y-%m-%d %H:%M:%S')}")

        # Calculate time since last index
        time_diff = datetime.now() - last_indexed
        if time_diff.days > 0:
            console.print(f"[yellow]⚠️  {time_diff.days} day(s) ago - consider rebuilding[/]")
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            console.print(f"[green]✅ {hours} hour(s) ago - up to date[/]")
        else:
            console.print("[green]✅ Recently updated[/]")
    else:
        console.print("\n[red]❌ Never indexed[/]")
        console.print(f"[yellow]Run:[/] [cyan]zk-chat index rebuild --vault {vault_path}[/]")

    # Database directory info
    db_dir = os.path.join(vault_path, ".zk_chat_db")
    if os.path.exists(db_dir):
        # Calculate directory size
        total_size = 0
        file_count = 0
        for dirpath, dirnames, filenames in os.walk(db_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
                file_count += 1

        # Convert to readable format
        if total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        elif total_size < 1024 * 1024 * 1024:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{total_size / (1024 * 1024 * 1024):.1f} GB"

        console.print(f"\n[bold]Index Database:[/]")
        console.print(f"  • Location: {db_dir}")
        console.print(f"  • Size: {size_str}")
        console.print(f"  • Files: {file_count}")
    else:
        console.print(f"\n[yellow]⚠️  No index database found[/]")

    # Count markdown files in vault
    markdown_count = 0
    for root, dirs, files in os.walk(vault_path):
        # Skip database directory
        if '.zk_chat_db' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                markdown_count += 1

    console.print(f"\n[bold]Vault Statistics:[/]")
    console.print(f"  • Markdown files: {markdown_count}")

    if last_indexed and markdown_count > 0:
        console.print(f"\n[green]✅ Index appears healthy[/]")
    elif markdown_count == 0:
        console.print(f"\n[yellow]⚠️  No markdown files found in vault[/]")
    else:
        console.print(f"\n[red]❌ Index needs rebuilding[/]")
        console.print("[dim]Run: [cyan]zk-chat index rebuild[/dim]")


# Default command
@index_app.callback()
def index_default(ctx: typer.Context):
    """
    Manage your Zettelkasten search index.

    The index enables fast semantic search across your notes.
    Use [cyan]rebuild[/] to update it and [cyan]status[/] to check its health.
    """
    if ctx.invoked_subcommand is None:
        # Show help by default
        console.print(ctx.get_help())
        console.print("\n[yellow]💡 Tip:[/] Use [cyan]zk-chat index --help[/] to see available commands.")
        console.print("Most common: [cyan]zk-chat index rebuild[/] or [cyan]zk-chat index status[/]")