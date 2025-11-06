"""
Bookmarks subcommand for zk-chat.

Manages vault bookmarks for quick access to your Zettelkasten vaults.
"""
import typer
from rich.console import Console
from rich.table import Table

from zk_chat.global_config import GlobalConfig

bookmarks_app = typer.Typer(
    name="bookmarks",
    help="🔖 Manage vault bookmarks",
    rich_markup_mode="rich"
)

console = Console()


@bookmarks_app.command()
def list():
    """
    List all vault bookmarks.

    [bold]Examples:[/]

    • [cyan]zk-chat bookmarks list[/] - Show all bookmarked vaults
    """
    global_config = GlobalConfig.load()

    if not global_config.bookmarks:
        console.print("[yellow]No bookmarks found.[/]")
        console.print("\n[dim]Add a bookmark with:[/]")
        console.print("  [cyan]zk-chat interactive --vault /path/to/vault --save[/]")
        return

    # Create a table for better formatting
    table = Table(title="Vault Bookmarks", show_header=True, header_style="bold cyan")
    table.add_column("Path", style="green")
    table.add_column("Status", style="dim")

    for path in global_config.bookmarks:
        status = "last opened" if path == global_config.last_opened_bookmark else ""
        table.add_row(path, status)

    console.print(table)
    console.print(f"\n[dim]Total: {len(global_config.bookmarks)} bookmark(s)[/]")


@bookmarks_app.command()
def remove(
        path: str = typer.Argument(help="Path to the vault bookmark to remove (can be relative)")
):
    """
    Remove a vault bookmark.

    [bold]Examples:[/]

    • [cyan]zk-chat bookmarks remove ~/notes[/] - Remove bookmark for ~/notes
    • [cyan]zk-chat bookmarks remove /absolute/path/to/vault[/] - Remove by absolute path
    """
    import os

    abs_path = os.path.abspath(path)
    global_config = GlobalConfig.load()

    if global_config.remove_bookmark(abs_path):
        console.print(f"[green]✅ Bookmark removed:[/] {abs_path}")
    else:
        console.print(f"[red]❌ Error:[/] Bookmark not found for '{abs_path}'")
        console.print("\n[dim]Use [cyan]zk-chat bookmarks list[/dim] to see available bookmarks.")
        raise typer.Exit(1)


@bookmarks_app.callback()
def bookmarks_default(ctx: typer.Context):
    """
    Manage vault bookmarks for quick access.

    Bookmarks allow you to quickly switch between multiple Zettelkasten vaults
    without specifying the full path each time.
    """
    if ctx.invoked_subcommand is None:
        # Show help by default
        console.print(ctx.get_help())
        console.print(
            "\n[yellow]💡 Tip:[/] Use [cyan]zk-chat bookmarks list[/] to see your bookmarked "
            "vaults.")
