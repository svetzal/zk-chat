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

import typer
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated
import sys

# Import subcommands
from zk_chat.commands.gui import gui_app
from zk_chat.commands.index import index_app

# Import functions for interactive and query commands
from zk_chat.cli import common_init_typer, display_banner
from zk_chat.chat import chat as run_chat
from zk_chat.agent import agent as run_agent

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

# Global options that apply to all commands
console = Console()


def create_args_namespace(
    vault: Optional[Path] = None,
    save: bool = False,
    gateway: Optional[str] = None,
    model: Optional[str] = None,
    visual_model: Optional[str] = None,
    reindex: bool = False,
    full: bool = False,
    unsafe: bool = False,
    git: bool = False,
    store_prompt: bool = True,
    reset_memory: bool = False,
    remove_bookmark: Optional[str] = None,
    list_bookmarks: bool = False,
):
    """Create a namespace object similar to argparse for common_init_typer."""
    class Args:
        def __init__(self):
            self.vault = str(vault) if vault else None
            self.save = save
            self.gateway = gateway
            self.model = model
            self.visual_model = visual_model
            self.reindex = reindex
            self.full = full
            self.unsafe = unsafe
            self.git = git
            self.store_prompt = store_prompt
            self.reset_memory = reset_memory
            self.remove_bookmark = remove_bookmark
            self.list_bookmarks = list_bookmarks

    return Args()


@app.command()
def interactive(
    # Vault options
    vault: Annotated[Optional[Path], typer.Option("--vault", "-v", help="Path to your Zettelkasten vault")] = None,
    save: Annotated[bool, typer.Option("--save", help="Save the vault path as a bookmark")] = False,

    # Model options
    gateway: Annotated[Optional[str], typer.Option("--gateway", "-g", help="Model gateway (ollama/openai)")] = None,
    model: Annotated[Optional[str], typer.Option("--model", "-m", help="Chat model to use")] = None,
    visual_model: Annotated[Optional[str], typer.Option("--visual-model", help="Visual analysis model")] = None,

    # Index options
    reindex: Annotated[bool, typer.Option("--reindex", help="Reindex before starting chat")] = False,
    full: Annotated[bool, typer.Option("--full", help="Force full reindex (with --reindex)")] = False,

    # Chat options
    unsafe: Annotated[bool, typer.Option("--unsafe", help="Allow AI to modify your Zettelkasten")] = False,
    git: Annotated[bool, typer.Option("--git", help="Enable git integration")] = False,
    store_prompt: Annotated[bool, typer.Option("--store-prompt/--no-store-prompt", help="Store system prompt in vault")] = True,

    # Agent mode
    agent_mode: Annotated[bool, typer.Option("--agent", help="Use agent mode (autonomous problem solving)")] = False,

    # Memory options
    reset_memory: Annotated[bool, typer.Option("--reset-memory", help="Clear smart memory")] = False,

    # Bookmark management
    remove_bookmark: Annotated[Optional[str], typer.Option("--remove-bookmark", help="Remove bookmark")] = None,
    list_bookmarks: Annotated[bool, typer.Option("--list-bookmarks", help="List all bookmarks")] = False,
):
    """
    Start an interactive chat session with your Zettelkasten.

    [bold]Examples:[/]

    • [cyan]zk-chat interactive --vault ~/notes[/] - Start chat with specific vault
    • [cyan]zk-chat interactive --agent[/] - Use autonomous agent mode
    • [cyan]zk-chat interactive --unsafe --git[/] - Allow AI to edit files with git tracking
    • [cyan]zk-chat interactive --reindex[/] - Rebuild index before starting

    [bold]Agent mode vs Chat mode:[/]

    • [green]Chat mode[/]: Simple Q&A with your notes
    • [green]Agent mode[/]: Autonomous problem-solving with full tool access
    """
    # Create args namespace using shared function
    args = create_args_namespace(
        vault=vault,
        save=save,
        gateway=gateway,
        model=model,
        visual_model=visual_model,
        reindex=reindex,
        full=full,
        unsafe=unsafe,
        git=git,
        store_prompt=store_prompt,
        reset_memory=reset_memory,
        remove_bookmark=remove_bookmark,
        list_bookmarks=list_bookmarks,
    )

    # Use common initialization logic
    config = common_init_typer(args)
    if not config:
        return

    # Display appropriate banner
    if agent_mode:
        display_banner(config, title="ZkChat Agent", unsafe=unsafe, use_git=git, store_prompt=store_prompt)
        run_agent(config)
    else:
        display_banner(config, title="ZkChat", unsafe=unsafe, use_git=git, store_prompt=store_prompt)
        run_chat(config, unsafe=unsafe, use_git=git, store_prompt=store_prompt)


@app.command()
def query(
    prompt: Annotated[Optional[str], typer.Argument(help="Query to ask your Zettelkasten (or read from STDIN if not provided)")] = None,
    vault: Annotated[Optional[Path], typer.Option("--vault", "-v", help="Path to your Zettelkasten vault")] = None,
    gateway: Annotated[Optional[str], typer.Option("--gateway", "-g", help="Model gateway (ollama/openai)")] = None,
    model: Annotated[Optional[str], typer.Option("--model", "-m", help="Chat model to use")] = None,
    agent_mode: Annotated[bool, typer.Option("--agent/--no-agent", help="Use agent mode for complex queries")] = True,
):
    """
    Ask a single question to your Zettelkasten and get an answer.

    Can read input from command line argument or STDIN.

    [bold]Examples:[/]

    • [cyan]zk-chat query "What are my thoughts on productivity?"[/]
    • [cyan]cat prompt.txt | zk-chat query[/]
    • [cyan]echo "My question" | zk-chat query --agent[/]
    • [cyan]zk-chat query "Find connections" --vault ~/notes[/]

    Agent mode is recommended for complex queries that might require multiple steps.
    """

    # Get prompt from argument or STDIN
    if prompt is None:
        if sys.stdin.isatty():
            console.print("[red]Error:[/] No prompt provided. Either pass a prompt as an argument or pipe input via STDIN.")
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

    # Create args namespace using shared function with query-specific defaults
    args = create_args_namespace(
        vault=vault,
        save=False,
        gateway=gateway,
        model=model,
        visual_model=None,
        reindex=False,
        full=False,
        unsafe=False,
        git=False,
        store_prompt=True,
        reset_memory=False,
        remove_bookmark=None,
        list_bookmarks=False,
    )
    config = common_init_typer(args)
    if not config:
        return

    # Execute single query
    if agent_mode:
        console.print(f"[bold cyan]Query:[/] {prompt}")
        console.print("[dim]Using agent mode for autonomous problem solving...[/]\n")

        # Import and run agent with single query
        from zk_chat.agent import agent_single_query
        result = agent_single_query(config, prompt)
        console.print(f"\n[bold green]Response:[/]\n{result}")
    else:
        # Simple chat query
        console.print(f"[bold cyan]Query:[/] {prompt}")
        console.print("[dim]Using simple chat mode...[/]\n")

        from zk_chat.chat import chat_single_query
        result = chat_single_query(config, prompt)
        console.print(f"\n[bold green]Response:[/]\n{result}")


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[bool, typer.Option("--version", help="Show version information")] = False,
):
    """
    💬 Chat with your Zettelkasten - AI-powered knowledge management

    Use [bold cyan]zk-chat COMMAND --help[/] to see options for specific commands.

    [bold]Common workflows:[/]

    • [cyan]zk-chat interactive[/] - Start interactive chat session
    • [cyan]zk-chat query "your question"[/] - Ask a single question
    • [cyan]zk-chat gui[/] - Launch graphical interface
    • [cyan]zk-chat index --reindex[/] - Rebuild search index

    [bold]Getting started:[/]

    1. Set up your vault: [cyan]zk-chat interactive --vault /path/to/notes[/]
    2. Chat with your notes: [cyan]zk-chat interactive[/]
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