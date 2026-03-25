"""
GUI subcommand for zk-chat.

Launches the graphical user interface.
"""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

import zk_chat.bootstrap  # noqa: F401  # Sets CHROMA_TELEMETRY and logging before chromadb imports

gui_app = typer.Typer(name="gui", help="🖥️ Launch the graphical user interface", rich_markup_mode="rich")

console = Console()


@gui_app.command()
def launch(
    vault: Annotated[Path | None, typer.Option("--vault", "-v", help="Path to your Zettelkasten vault")] = None,
):
    """
    Launch the graphical user interface for zk-chat.

    [bold yellow]⚠️  Note:[/] The GUI is experimental and may not work as expected.

    [bold]Features:[/]

    • Multi-line chat input
    • Scrollable chat history
    • Visual model selection
    • Vault configuration

    [bold]Examples:[/]

    • [cyan]zk-chat gui launch[/] - Launch GUI with last used vault
    • [cyan]zk-chat gui launch --vault ~/notes[/] - Launch with specific vault
    """
    try:
        from zk_chat.qt import main as run_gui

        console.print("[yellow]⚠️  [bold]Experimental Feature[/][/]")
        console.print("[dim]The GUI is experimental and may not work as expected.[/]")
        console.print("[dim]It uses the older configuration method.[/]\n")

        console.print("[green]🚀 Launching zk-chat GUI...[/]")

        # Note: The current GUI implementation doesn't use the same config system
        # as the CLI commands, so we can't easily pass the vault parameter
        if vault:
            console.print(f"[yellow]Note:[/] Vault parameter ({vault}) will be ignored.")
            console.print("[yellow]Configure the vault through the GUI settings menu.[/]\n")

        run_gui()

    except ImportError as e:
        console.print("[red]❌ Error:[/] GUI dependencies not available")
        console.print(f"[dim]Details: {e}[/]")
        console.print("\n[yellow]Try installing GUI dependencies:[/]")
        console.print("[cyan]pip install 'zk-chat[gui]'[/]")
        raise typer.Exit(1) from e

    except Exception as e:
        console.print(f"[red]❌ Error launching GUI:[/] {e}")
        raise typer.Exit(1) from e


# Default command (launch)
@gui_app.callback()
def gui_default(ctx: typer.Context):
    """
    Launch the graphical user interface.

    If no subcommand is provided, launches the GUI.
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(launch)
