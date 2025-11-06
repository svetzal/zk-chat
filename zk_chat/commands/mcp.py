"""
MCP subcommand for zk-chat.

Manages MCP (Model Context Protocol) server connections.
"""

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from zk_chat.global_config import GlobalConfig, MCPServerConfig, MCPServerType
from zk_chat.mcp_client import verify_mcp_server

mcp_app = typer.Typer(
    name="mcp",
    help="🔌 Manage MCP (Model Context Protocol) server connections",
    rich_markup_mode="rich"
)

console = Console()


@mcp_app.command()
def add(
        name: Annotated[str, typer.Argument(help="Name for this MCP server")],
        server_type: Annotated[
            str, typer.Option("--type", "-t", help="Server type (stdio or http)")],
        command: Annotated[
            str | None, typer.Option("--command", "-c", help="Command for STDIO server")] = None,
        url: Annotated[str | None, typer.Option("--url", "-u", help="URL for HTTP server")] = None,
        args: Annotated[str | None, typer.Option("--args", "-a",
                                                 help="Command line arguments ("
                                                      "comma-separated)")] = None,
        no_verify: Annotated[bool, typer.Option("--no-verify",
                                                help="Skip server availability verification")] =
                                                False,
):
    """
    Add a new MCP server connection.

    [bold]Server Types:[/]

    • [green]stdio[/]: Connect via STDIO to a local command
    • [green]http[/]: Connect via HTTP to a remote server

    [bold]Examples:[/]

    • [cyan]zk-chat mcp add figma --type stdio --command figma-mcp[/]
    • [cyan]zk-chat mcp add chrome --type http --url http://localhost:8080[/]
    • [cyan]zk-chat mcp add custom --type stdio --command my-mcp --args "--flag1,--flag2"[/]

    [bold yellow]💡 Tip:[/] Use --no-verify to skip availability check during registration.
    """
    srv_type = _validate_server_type(server_type)
    _validate_required_params(srv_type, command, url)

    args_list = []
    if args:
        args_list = [arg.strip() for arg in args.split(",") if arg.strip()]

    server_config = _create_server_config(name, srv_type, command, url, args_list)

    if not no_verify:
        _verify_server(name, server_config)

    _register_server(server_config)
    _display_registration_success(name, srv_type, command, url, args_list)


def _validate_server_type(server_type: str) -> MCPServerType:
    """Validate and return the server type."""
    try:
        return MCPServerType(server_type.lower())
    except ValueError as e:
        console.print(
            f"[red]❌ Error:[/] Invalid server type '{server_type}'. Use 'stdio' or 'http'.")
        raise typer.Exit(1) from e


def _validate_required_params(srv_type: MCPServerType, command: str | None,
                              url: str | None) -> None:
    """Validate required parameters based on server type."""
    if srv_type == MCPServerType.STDIO and not command:
        console.print("[red]❌ Error:[/] STDIO server requires --command parameter.")
        raise typer.Exit(1)

    if srv_type == MCPServerType.HTTP and not url:
        console.print("[red]❌ Error:[/] HTTP server requires --url parameter.")
        raise typer.Exit(1)


def _create_server_config(
        name: str,
        srv_type: MCPServerType,
        command: str | None,
        url: str | None,
        args_list: list
) -> MCPServerConfig:
    """Create server configuration."""
    try:
        return MCPServerConfig(
            name=name,
            server_type=srv_type,
            command=command,
            url=url,
            args=args_list
        )
    except ValueError as e:
        console.print(f"[red]❌ Error:[/] {str(e)}")
        raise typer.Exit(1) from e


def _verify_server(name: str, server_config: MCPServerConfig) -> None:
    """Verify server availability."""
    console.print(f"[dim]Verifying {name} server availability...[/]")
    if verify_mcp_server(server_config):
        console.print(f"[green]✅ Server {name} is available[/]")
    else:
        console.print(f"[red]❌ Server {name} is not available[/]")
        console.print(
            "[yellow]Use --no-verify to register anyway, or fix the server configuration.[/]")
        raise typer.Exit(1)


def _register_server(server_config: MCPServerConfig) -> None:
    """Register server in global config."""
    global_config = GlobalConfig.load()
    global_config.add_mcp_server(server_config)


def _display_registration_success(
        name: str,
        srv_type: MCPServerType,
        command: str | None,
        url: str | None,
        args_list: list
) -> None:
    """Display success message and configuration."""
    console.print(f"\n[green]✅ MCP server '{name}' registered successfully![/]")

    console.print("\n[bold]Server Configuration:[/]")
    console.print(f"  • Name: {name}")
    console.print(f"  • Type: {srv_type.value}")
    if command:
        console.print(f"  • Command: {command}")
    if url:
        console.print(f"  • URL: {url}")
    if args_list:
        args_str = ', '.join(args_list)
        console.print(f"  • Args: {args_str}")


@mcp_app.command()
def remove(
        name: Annotated[str, typer.Argument(help="Name of the MCP server to remove")],
):
    """
    Remove a registered MCP server.

    [bold]Examples:[/]

    • [cyan]zk-chat mcp remove figma[/]
    • [cyan]zk-chat mcp remove chrome[/]
    """
    global_config = GlobalConfig.load()

    if global_config.remove_mcp_server(name):
        console.print(f"[green]✅ MCP server '{name}' removed successfully![/]")
    else:
        console.print(f"[red]❌ Error:[/] MCP server '{name}' not found.")
        console.print("[dim]Use [cyan]zk-chat mcp list[/dim] to see registered servers.")
        raise typer.Exit(1)


@mcp_app.command()
def list():
    """
    List all registered MCP servers.

    [bold]Examples:[/]

    • [cyan]zk-chat mcp list[/]
    """
    global_config = GlobalConfig.load()
    servers = global_config.list_mcp_servers()

    if not servers:
        console.print("[yellow]No MCP servers registered.[/]")
        console.print(
            "\n[dim]Add a server with:[/] [cyan]zk-chat mcp add <name> --type <stdio|http> ...[/]")
        return

    # Create a table
    table = Table(title="Registered MCP Servers", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green", no_wrap=True)
    table.add_column("Type", style="yellow")
    table.add_column("Configuration", style="white")
    table.add_column("Status", style="magenta")

    # Populate table
    for server in servers:
        config_str = ""
        if server.server_type == MCPServerType.STDIO:
            config_str = f"Command: {server.command}"
            if server.args:
                config_str += f"\nArgs: {', '.join(server.args)}"
        else:
            config_str = f"URL: {server.url}"

        # Check availability
        is_available = verify_mcp_server(server)
        status = "✅ Available" if is_available else "❌ Unavailable"

        table.add_row(
            server.name,
            server.server_type.value,
            config_str,
            status
        )

    console.print(table)

    # Check if any servers are unavailable
    unavailable = [s for s in servers if not verify_mcp_server(s)]
    if unavailable:
        console.print(f"\n[yellow]⚠️  Warning: {len(unavailable)} server(s) unavailable[/]")
        console.print("[dim]These servers may not work during chat sessions.[/]")


@mcp_app.command()
def verify(
        name: Annotated[str | None, typer.Argument(
            help="Name of the MCP server to verify (or all if not specified)")] = None,
):
    """
    Verify the availability of MCP servers.

    [bold]Examples:[/]

    • [cyan]zk-chat mcp verify[/] - Verify all servers
    • [cyan]zk-chat mcp verify figma[/] - Verify specific server
    """
    global_config = GlobalConfig.load()

    if name:
        # Verify specific server
        server = global_config.get_mcp_server(name)
        if not server:
            console.print(f"[red]❌ Error:[/] MCP server '{name}' not found.")
            raise typer.Exit(1)

        console.print(f"[dim]Verifying {name} server...[/]")
        if verify_mcp_server(server):
            console.print(f"[green]✅ Server '{name}' is available[/]")
        else:
            console.print(f"[red]❌ Server '{name}' is not available[/]")
            raise typer.Exit(1)
    else:
        # Verify all servers
        servers = global_config.list_mcp_servers()
        if not servers:
            console.print("[yellow]No MCP servers registered.[/]")
            return

        console.print(f"[dim]Verifying {len(servers)} server(s)...[/]\n")

        all_available = True
        for server in servers:
            is_available = verify_mcp_server(server)
            status = "[green]✅[/]" if is_available else "[red]❌[/]"
            console.print(f"{status} {server.name} ({server.server_type.value})")
            if not is_available:
                all_available = False

        if all_available:
            console.print("\n[green]✅ All servers are available[/]")
        else:
            console.print("\n[yellow]⚠️  Some servers are unavailable[/]")
            raise typer.Exit(1)


@mcp_app.callback()
def mcp_default(ctx: typer.Context):
    """
    Manage MCP (Model Context Protocol) server connections.

    MCP servers allow zk-chat to connect to external tools and services
    like Figma, Chrome DevTools, and other MCP-compatible systems.
    """
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        console.print(
            "\n[yellow]💡 Tip:[/] Use [cyan]zk-chat mcp --help[/] to see available commands.")
        console.print(
            "Most common: [cyan]zk-chat mcp add[/], [cyan]zk-chat mcp list[/], or [cyan]zk-chat mcp verify[/]")
