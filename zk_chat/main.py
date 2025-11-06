# ruff: noqa: E402  # Configure logging/env before imports to reduce noisy logs and disable telemetry
"""
Main CLI interface for zk-chat using Typer.

This provides a modern, discoverable CLI with commands:
- zk-chat interactive  # Interactive chat with your Zettelkasten
- zk-chat query       # Ask a single question
- zk-chat gui         # Launch the graphical interface
- zk-chat index       # Index management operations
"""
import logging
import os

# Set logging levels early to prevent chatty output
logging.basicConfig(level=logging.WARN)

# Disable ChromaDB telemetry to avoid PostHog compatibility issues
os.environ['CHROMA_TELEMETRY'] = 'false'

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from zk_chat.agent import agent as run_agent

# Import functions for interactive and query commands
from zk_chat.cli import common_init_typer, display_banner
from zk_chat.commands.bookmarks import bookmarks_app
from zk_chat.commands.diagnose import diagnose_app

# Import subcommands
from zk_chat.commands.gui import gui_app
from zk_chat.commands.index import index_app
from zk_chat.commands.mcp import mcp_app

# Create the main app
app = typer.Typer(
    name="zk-chat",
    help="💬 Chat with your Zettelkasten - AI-powered knowledge management",
    rich_markup_mode="rich",
    no_args_is_help=True,
    pretty_exceptions_enable=False,  # We handle our own exceptions
)

# Add subcommands
app.add_typer(gui_app, name="gui")
app.add_typer(index_app, name="index")
app.add_typer(mcp_app, name="mcp")
app.add_typer(diagnose_app, name="diagnose")
app.add_typer(bookmarks_app, name="bookmarks")

# Global options that apply to all commands
console = Console()


def create_args_namespace(
    vault: Path | None = None,
    save: bool = False,
    gateway: str | None = None,
    model: str | None = None,
    visual_model: str | None = None,
    no_index: bool = False,
    unsafe: bool = False,
    git: bool = False,
    store_prompt: bool = True,
    reset_memory: bool = False,
):
    """Create a namespace object similar to argparse for common_init_typer."""

    class Args:
        def __init__(self):
            self.vault = str(vault) if vault else None
            self.save = save
            self.gateway = gateway
            self.model = model
            self.visual_model = visual_model
            self.reindex = not no_index  # Index by default unless --no-index is set
            self.full = False  # Never do full reindex on startup
            self.unsafe = unsafe
            self.git = git
            self.store_prompt = store_prompt
            self.reset_memory = reset_memory
            self.remove_bookmark = None
            self.list_bookmarks = False

    return Args()


@app.command()
def interactive(
    # Vault options
    vault: Annotated[Path | None, typer.Option("--vault", "-v",
                                               help="Path to your Zettelkasten vault")] = None,
    save: Annotated[
        bool, typer.Option("--save", help="Save the vault path as a bookmark")] = False,

    # Model options
    gateway: Annotated[str | None, typer.Option("--gateway", "-g",
                                                help="Model gateway (ollama/openai)")] = None,
    model: Annotated[
        str | None, typer.Option("--model", "-m", help="Chat model to use")] = None,
    visual_model: Annotated[
        str | None, typer.Option("--visual-model", help="Visual analysis model")] = None,

    # Index options
    no_index: Annotated[bool, typer.Option("--no-index",
                                           help="Skip indexing new documents on startup")] =
    False,

    # Agent options
    unsafe: Annotated[
        bool, typer.Option("--unsafe", help="Allow AI to modify your Zettelkasten")] = False,
    git: Annotated[bool, typer.Option("--git", help="Enable git integration")] = False,
    store_prompt: Annotated[bool, typer.Option("--store-prompt/--no-store-prompt",
                                               help="Store system prompt in vault")] = True,

    # Memory options
    reset_memory: Annotated[
        bool, typer.Option("--reset-memory", help="Clear smart memory")] = False,
):
    """
    Start an interactive agent session with your Zettelkasten.

    The agent uses autonomous problem-solving with full tool access to help you
    work with your knowledge base. Continue chatting until you exit.

    [bold]Examples:[/]

    • [cyan]zk-chat interactive --vault ~/notes[/] - Start agent with specific vault
    • [cyan]zk-chat interactive --unsafe --git[/] - Allow AI to edit files with git tracking
    • [cyan]zk-chat interactive --no-index[/] - Skip indexing new documents on startup
    """
    # Create args namespace using shared function
    args = create_args_namespace(
        vault=vault,
        save=save,
        gateway=gateway,
        model=model,
        visual_model=visual_model,
        no_index=no_index,
        unsafe=unsafe,
        git=git,
        store_prompt=store_prompt,
        reset_memory=reset_memory,
    )

    # Use common initialization logic
    config = common_init_typer(args)
    if not config:
        return

    # Display banner and run agent
    display_banner(config, title="ZkChat Agent", unsafe=unsafe, use_git=git,
                   store_prompt=store_prompt)
    run_agent(config)


@app.command()
def query(
    prompt: Annotated[str | None, typer.Argument(
        help="Query to ask your Zettelkasten (or read from STDIN if not provided)")] = None,

    # Vault options
    vault: Annotated[Path | None, typer.Option("--vault", "-v",
                                               help="Path to your Zettelkasten vault")] = None,
    save: Annotated[
        bool, typer.Option("--save", help="Save the vault path as a bookmark")] = False,

    # Model options
    gateway: Annotated[str | None, typer.Option("--gateway", "-g",
                                                help="Model gateway (ollama/openai)")] = None,
    model: Annotated[
        str | None, typer.Option("--model", "-m", help="Chat model to use")] = None,
    visual_model: Annotated[
        str | None, typer.Option("--visual-model", help="Visual analysis model")] = None,

    # Index options
    no_index: Annotated[
        bool, typer.Option("--no-index", help="Skip indexing new documents")] = False,

    # Agent options
    unsafe: Annotated[
        bool, typer.Option("--unsafe", help="Allow AI to modify your Zettelkasten")] = False,
    git: Annotated[bool, typer.Option("--git", help="Enable git integration")] = False,
    store_prompt: Annotated[bool, typer.Option("--store-prompt/--no-store-prompt",
                                               help="Store system prompt in vault")] = True,

    # Memory options
    reset_memory: Annotated[
        bool, typer.Option("--reset-memory", help="Clear smart memory")] = False,
):
    """
    Ask a single question to your Zettelkasten and exit.

    The agent uses autonomous problem-solving with full tool access to help you
    work with your knowledge base. Answers your query and exits.

    Can read input from command line argument or STDIN.

    [bold]Examples:[/]

    • [cyan]zk-chat query "What are my thoughts on productivity?"[/]
    • [cyan]cat prompt.txt | zk-chat query[/]
    • [cyan]echo "My question" | zk-chat query[/]
    • [cyan]zk-chat query "Find connections" --vault ~/notes[/]
    • [cyan]zk-chat query "Update my notes" --unsafe --git[/]
    """

    # Get prompt from argument or STDIN
    if prompt is None:
        if sys.stdin.isatty():
            console.print(
                "[red]Error:[/] No prompt provided. Either pass a prompt as an argument or pipe "
                "input via STDIN.")
            console.print("Examples:")
            console.print("  [cyan]zk-chat query \"Your question here\"[/]")
            console.print("  [cyan]cat prompt.txt | zk-chat query[/]")
            raise typer.Exit(1)
        else:
            # Read from STDIN
            prompt = sys.stdin.read().strip()
            if not prompt:
                console.print("[red]Error:[/] No input received from STDIN.")
                raise typer.Exit(1)

    # Create args namespace using shared function
    args = create_args_namespace(
        vault=vault,
        save=save,
        gateway=gateway,
        model=model,
        visual_model=visual_model,
        no_index=no_index,
        unsafe=unsafe,
        git=git,
        store_prompt=store_prompt,
        reset_memory=reset_memory,
    )
    config = common_init_typer(args)
    if not config:
        return

    # Display banner if using unsafe or git modes
    if unsafe or git:
        display_banner(config, title="ZkChat Query", unsafe=unsafe, use_git=git,
                       store_prompt=store_prompt)

    # Execute single query using agent
    console.print(f"[bold cyan]Query:[/] {prompt}")
    console.print("[dim]Using agent for autonomous problem solving...[/]\n")

    # Import and run agent with single query
    from zk_chat.agent import agent_single_query
    result = agent_single_query(config, prompt)
    console.print(f"\n[bold green]Response:[/]\n{result}")


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        bool, typer.Option("--version", help="Show version information")] = False,
):
    """
    💬 ZkChat - AI Agent for your Zettelkasten

    Use [bold cyan]zk-chat COMMAND --help[/] to see options for specific commands.

    [bold]Common workflows:[/]

    • [cyan]zk-chat interactive[/] - Start interactive agent session
    • [cyan]zk-chat query "your question"[/] - Ask a single question
    • [cyan]zk-chat gui[/] - Launch graphical interface
    • [cyan]zk-chat index update[/] - Update search index
    • [cyan]zk-chat diagnose index[/] - Troubleshoot index issues
    • [cyan]zk-chat mcp list[/] - Manage MCP server connections

    [bold]Getting started:[/]

    1. Set up your vault: [cyan]zk-chat interactive --vault /path/to/notes[/]
    2. Work with your agent: [cyan]zk-chat interactive[/]
    3. For visual interface: [cyan]zk-chat gui[/]
    """
    if version:
        from importlib.metadata import version as get_version
        try:
            pkg_version = get_version("zk-chat")
        except Exception:
            pkg_version = "unknown"

        console.print(Panel(
            f"[bold cyan]zk-chat[/] version [green]{pkg_version}[/]\n"
            f"[dim]Copyright (C) 2024-2025 Stacey Vetzal[/]",
            title="Version Information",
            border_style="cyan"
        ))
        raise typer.Exit()


if __name__ == "__main__":
    app()
