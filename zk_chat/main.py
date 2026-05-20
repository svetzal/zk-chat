"""
Main CLI interface for zk-chat using Typer.

This provides a modern, discoverable CLI with commands:
- zk-chat interactive  # Interactive chat with your Zettelkasten
- zk-chat query       # Ask a single question
- zk-chat gui         # Launch the graphical interface
- zk-chat index       # Index management operations
"""

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel

import zk_chat.bootstrap  # noqa: F401  # Sets CHROMA_TELEMETRY and logging before chromadb imports
from zk_chat.agent import agent as run_agent
from zk_chat.agent import agent_single_query
from zk_chat.cli import common_init, display_banner
from zk_chat.commands.bookmarks import bookmarks_app
from zk_chat.commands.diagnose import diagnose_app
from zk_chat.commands.gui import gui_app
from zk_chat.commands.index import index_app
from zk_chat.commands.mcp import mcp_app
from zk_chat.gateway_defaults import (
    create_default_config_gateway,
    create_default_console_gateway,
    create_default_global_config_gateway,
)
from zk_chat.init_options import InitOptions

app = typer.Typer(
    name="zk-chat",
    help="💬 Chat with your Zettelkasten - AI-powered knowledge management",
    rich_markup_mode="rich",
    no_args_is_help=True,
    pretty_exceptions_enable=False,  # We handle our own exceptions
)

VaultOption = Annotated[Path | None, typer.Option("--vault", "-v", help="Path to your Zettelkasten vault")]
SaveOption = Annotated[bool, typer.Option("--save", help="Save the vault path as a bookmark")]
GatewayOption = Annotated[str | None, typer.Option("--gateway", "-g", help="Model gateway (ollama/openai)")]
ModelOption = Annotated[str | None, typer.Option("--model", "-m", help="Chat model to use")]
VisualModelOption = Annotated[str | None, typer.Option("--visual-model", help="Visual analysis model")]
NoIndexOption = Annotated[bool, typer.Option("--no-index", help="Skip indexing new documents on startup")]
UnsafeOption = Annotated[bool, typer.Option("--unsafe", help="Allow AI to modify your Zettelkasten")]
GitOption = Annotated[bool, typer.Option("--git", help="Enable git integration")]
StorePromptOption = Annotated[
    bool, typer.Option("--store-prompt/--no-store-prompt", help="Store system prompt in vault")
]
ResetMemoryOption = Annotated[bool, typer.Option("--reset-memory", help="Clear smart memory")]


def _build_init_options(
    vault: Path | None,
    save: bool,
    gateway: str | None,
    model: str | None,
    visual_model: str | None,
    no_index: bool,
    unsafe: bool,
    git: bool,
    store_prompt: bool,
    reset_memory: bool,
) -> InitOptions:
    return InitOptions(
        vault=str(vault) if vault else None,
        save=save,
        gateway=gateway,
        model=model,
        visual_model=visual_model,
        reindex=not no_index,
        unsafe=unsafe,
        git=git,
        store_prompt=store_prompt,
        reset_memory=reset_memory,
    )

app.add_typer(gui_app, name="gui")
app.add_typer(index_app, name="index")
app.add_typer(mcp_app, name="mcp")
app.add_typer(diagnose_app, name="diagnose")
app.add_typer(bookmarks_app, name="bookmarks")


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[bool, typer.Option("--version", help="Show version information")] = False,
) -> None:
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
    ctx.ensure_object(dict)
    ctx.obj["console_gateway"] = create_default_console_gateway()
    ctx.obj["global_config_gateway"] = create_default_global_config_gateway()
    ctx.obj["config_gateway"] = create_default_config_gateway()

    if version:
        from importlib.metadata import PackageNotFoundError
        from importlib.metadata import version as get_version

        try:
            pkg_version = get_version("zk-chat")
        except PackageNotFoundError:
            pkg_version = "unknown"

        ctx.obj["console_gateway"].print(
            Panel(
                f"[bold cyan]zk-chat[/] version [green]{pkg_version}[/]\n[dim]Copyright (C) 2024-2025 Stacey Vetzal[/]",
                title="Version Information",
                border_style="cyan",
            )
        )
        raise typer.Exit()


@app.command()
def interactive(
    ctx: typer.Context,
    vault: VaultOption = None,
    save: SaveOption = False,
    gateway: GatewayOption = None,
    model: ModelOption = None,
    visual_model: VisualModelOption = None,
    no_index: NoIndexOption = False,
    unsafe: UnsafeOption = False,
    git: GitOption = False,
    store_prompt: StorePromptOption = True,
    reset_memory: ResetMemoryOption = False,
) -> None:
    """
    Start an interactive agent session with your Zettelkasten.

    The agent uses autonomous problem-solving with full tool access to help you
    work with your knowledge base. Continue chatting until you exit.

    [bold]Examples:[/]

    • [cyan]zk-chat interactive --vault ~/notes[/] - Start agent with specific vault
    • [cyan]zk-chat interactive --unsafe --git[/] - Allow AI to edit files with git tracking
    • [cyan]zk-chat interactive --no-index[/] - Skip indexing new documents on startup
    """
    _common_init = ctx.obj.get("common_init", common_init)
    _run_agent = ctx.obj.get("run_agent", run_agent)
    _display_banner = ctx.obj.get("display_banner", display_banner)

    options = _build_init_options(
        vault, save, gateway, model, visual_model, no_index, unsafe, git, store_prompt, reset_memory
    )
    global_config_gateway = ctx.obj["global_config_gateway"]
    config = _common_init(options, global_config_gateway, ctx.obj["config_gateway"], ctx.obj["console_gateway"])
    if not config:
        return

    _display_banner(
        config,
        ctx.obj["console_gateway"],
        title="ZkChat Agent",
        unsafe=unsafe,
        use_git=git,
        store_prompt=store_prompt,
    )
    _run_agent(config, global_config_gateway)


@app.command()
def query(
    ctx: typer.Context,
    prompt: Annotated[
        str | None, typer.Argument(help="Query to ask your Zettelkasten (or read from STDIN if not provided)")
    ] = None,
    vault: VaultOption = None,
    save: SaveOption = False,
    gateway: GatewayOption = None,
    model: ModelOption = None,
    visual_model: VisualModelOption = None,
    no_index: NoIndexOption = False,
    unsafe: UnsafeOption = False,
    git: GitOption = False,
    store_prompt: StorePromptOption = True,
    reset_memory: ResetMemoryOption = False,
) -> None:
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

    console_gateway = ctx.obj["console_gateway"]
    if prompt is None:
        if sys.stdin.isatty():
            console_gateway.print(
                "[red]Error:[/] No prompt provided. Either pass a prompt as an argument or pipe input via STDIN."
            )
            console_gateway.print("Examples:")
            console_gateway.print('  [cyan]zk-chat query "Your question here"[/]')
            console_gateway.print("  [cyan]cat prompt.txt | zk-chat query[/]")
            raise typer.Exit(1)
        else:
            prompt = sys.stdin.read().strip()
            if not prompt:
                console_gateway.print("[red]Error:[/] No input received from STDIN.")
                raise typer.Exit(1)

    options = _build_init_options(
        vault, save, gateway, model, visual_model, no_index, unsafe, git, store_prompt, reset_memory
    )
    global_config_gateway = ctx.obj["global_config_gateway"]
    config = common_init(options, global_config_gateway, ctx.obj["config_gateway"], ctx.obj["console_gateway"])
    if not config:
        return

    if unsafe or git:
        display_banner(
            config,
            console_gateway,
            title="ZkChat Query",
            unsafe=unsafe,
            use_git=git,
            store_prompt=store_prompt,
        )

    console_gateway.print(f"[bold cyan]Query:[/] {prompt}")
    console_gateway.print("[dim]Using agent for autonomous problem solving...[/]\n")

    result = agent_single_query(config, prompt, global_config_gateway)
    console_gateway.print(f"\n[bold green]Response:[/]\n{result}")


if __name__ == "__main__":
    app()
