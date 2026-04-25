"""
GUI subcommand for zk-chat.

Launches the graphical user interface.
"""

from pathlib import Path
from typing import Annotated

import typer

import zk_chat.bootstrap  # noqa: F401  # Sets CHROMA_TELEMETRY and logging before chromadb imports
from zk_chat.gateway_defaults import create_default_console_gateway

gui_app = typer.Typer(name="gui", help="🖥️ Launch the graphical user interface", rich_markup_mode="rich")


@gui_app.command()
def launch(
    vault: Annotated[Path | None, typer.Option("--vault", "-v", help="Path to your Zettelkasten vault")] = None,
) -> None:
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
    console_gateway = create_default_console_gateway()
    try:
        from zk_chat.qt import main as run_gui

        console_gateway.print("[yellow]⚠️  [bold]Experimental Feature[/][/]")
        console_gateway.print("[dim]The GUI is experimental and may not work as expected.[/]")
        console_gateway.print("[dim]It uses the older configuration method.[/]\n")

        console_gateway.print("[green]🚀 Launching zk-chat GUI...[/]")

        if vault:
            console_gateway.print(f"[yellow]Note:[/] Vault parameter ({vault}) will be ignored.")
            console_gateway.print("[yellow]Configure the vault through the GUI settings menu.[/]\n")

        run_gui()

    except ImportError as e:
        console_gateway.print("[red]❌ Error:[/] GUI dependencies not available")
        console_gateway.print(f"[dim]Details: {e}[/]")
        console_gateway.print("\n[yellow]Try installing GUI dependencies:[/]")
        console_gateway.print("[cyan]pip install 'zk-chat[gui]'[/]")
        raise typer.Exit(1) from e

    except (OSError, RuntimeError) as e:
        console_gateway.print(f"[red]❌ Error launching GUI:[/] {e}")
        raise typer.Exit(1) from e


@gui_app.callback()
def gui_default(ctx: typer.Context) -> None:
    """
    Launch the graphical user interface.

    If no subcommand is provided, launches the GUI.
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(launch)
