"""
MCP subcommand for zk-chat.

Manages MCP (Model Context Protocol) server connections.
"""

from typing import Annotated

import typer
from rich.table import Table

from zk_chat.console_service import ConsoleGateway
from zk_chat.gateway_defaults import create_default_console_gateway, create_default_global_config_gateway
from zk_chat.global_config import MCPServerType
from zk_chat.services.mcp_service import MCPService, MCPValidationError

mcp_app = typer.Typer(
    name="mcp", help="🔌 Manage MCP (Model Context Protocol) server connections", rich_markup_mode="rich"
)


@mcp_app.callback()
def mcp_default(ctx: typer.Context) -> None:
    """
    Manage MCP (Model Context Protocol) server connections.

    MCP servers allow zk-chat to connect to external tools and services
    like Figma, Chrome DevTools, and other MCP-compatible systems.
    """
    ctx.ensure_object(dict)
    ctx.obj["console_gateway"] = create_default_console_gateway()
    ctx.obj["global_config_gateway"] = create_default_global_config_gateway()
    if ctx.invoked_subcommand is None:
        console = ctx.obj["console_gateway"]
        console.print(ctx.get_help())
        console.print("\n[yellow]💡 Tip:[/] Use [cyan]zk-chat mcp --help[/] to see available commands.")
        console.print(
            "Most common: [cyan]zk-chat mcp add[/], [cyan]zk-chat mcp list[/], or [cyan]zk-chat mcp verify[/]"
        )


@mcp_app.command()
def add(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="Name for this MCP server")],
    server_type: Annotated[str, typer.Option("--type", "-t", help="Server type (stdio or http)")],
    command: Annotated[str | None, typer.Option("--command", "-c", help="Command for STDIO server")] = None,
    url: Annotated[str | None, typer.Option("--url", "-u", help="URL for HTTP server")] = None,
    args: Annotated[str | None, typer.Option("--args", "-a", help="Command line arguments (comma-separated)")] = None,
    no_verify: Annotated[bool, typer.Option("--no-verify", help="Skip server availability verification")] = False,
) -> None:
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
    console_gateway = ctx.obj["console_gateway"]
    service = MCPService(ctx.obj["global_config_gateway"])
    args_list = [arg.strip() for arg in args.split(",") if arg.strip()] if args else []

    try:
        server_config = service.register_server(name, server_type, command, url, args_list)
    except MCPValidationError as e:
        console_gateway.print(f"[red]❌ Error:[/] {e}")
        raise typer.Exit(1) from e

    if not no_verify:
        console_gateway.print(f"[dim]Verifying {name} server availability...[/]")
        if service.verify_server(server_config):
            console_gateway.print(f"[green]✅ Server {name} is available[/]")
        else:
            service.remove_server(name)
            console_gateway.print(f"[red]❌ Server {name} is not available[/]")
            console_gateway.print("[yellow]Use --no-verify to register anyway, or fix the server configuration.[/]")
            raise typer.Exit(1)

    _display_registration_success(name, server_config.server_type, command, url, args_list, console_gateway)


def _display_registration_success(
    name: str, srv_type: MCPServerType, command: str | None, url: str | None, args_list: list[str],
    console_gateway: ConsoleGateway,
) -> None:
    console_gateway.print(f"\n[green]✅ MCP server '{name}' registered successfully![/]")

    console_gateway.print("\n[bold]Server Configuration:[/]")
    console_gateway.print(f"  • Name: {name}")
    console_gateway.print(f"  • Type: {srv_type.value}")
    if command:
        console_gateway.print(f"  • Command: {command}")
    if url:
        console_gateway.print(f"  • URL: {url}")
    if args_list:
        args_str = ", ".join(args_list)
        console_gateway.print(f"  • Args: {args_str}")


@mcp_app.command()
def remove(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="Name of the MCP server to remove")],
) -> None:
    """
    Remove a registered MCP server.

    [bold]Examples:[/]

    • [cyan]zk-chat mcp remove figma[/]
    • [cyan]zk-chat mcp remove chrome[/]
    """
    console_gateway = ctx.obj["console_gateway"]
    service = MCPService(ctx.obj["global_config_gateway"])
    if service.remove_server(name):
        console_gateway.print(f"[green]✅ MCP server '{name}' removed successfully![/]")
    else:
        console_gateway.print(f"[red]❌ Error:[/] MCP server '{name}' not found.")
        console_gateway.print("[dim]Use [cyan]zk-chat mcp list[/dim] to see registered servers.")
        raise typer.Exit(1)


@mcp_app.command()
def list(ctx: typer.Context) -> None:
    """
    List all registered MCP servers.

    [bold]Examples:[/]

    • [cyan]zk-chat mcp list[/]
    """
    console_gateway = ctx.obj["console_gateway"]
    service = MCPService(ctx.obj["global_config_gateway"])
    servers = service.list_servers()

    if not servers:
        console_gateway.print("[yellow]No MCP servers registered.[/]")
        console_gateway.print("\n[dim]Add a server with:[/] [cyan]zk-chat mcp add <name> --type <stdio|http> ...[/]")
        return

    table = Table(title="Registered MCP Servers", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green", no_wrap=True)
    table.add_column("Type", style="yellow")
    table.add_column("Configuration", style="white")
    table.add_column("Status", style="magenta")

    for server in servers:
        config_str = ""
        if server.server_type == MCPServerType.STDIO:
            config_str = f"Command: {server.command}"
            if server.args:
                config_str += f"\nArgs: {', '.join(server.args)}"
        else:
            config_str = f"URL: {server.url}"

        is_available = service.verify_server(server)
        status = "✅ Available" if is_available else "❌ Unavailable"

        table.add_row(server.name, server.server_type.value, config_str, status)

    console_gateway.print(table)

    unavailable = [s for s in servers if not service.verify_server(s)]
    if unavailable:
        console_gateway.print(f"\n[yellow]⚠️  Warning: {len(unavailable)} server(s) unavailable[/]")
        console_gateway.print("[dim]These servers may not work during chat sessions.[/]")


@mcp_app.command()
def verify(
    ctx: typer.Context,
    name: Annotated[
        str | None, typer.Argument(help="Name of the MCP server to verify (or all if not specified)")
    ] = None,
) -> None:
    """
    Verify the availability of MCP servers.

    [bold]Examples:[/]

    • [cyan]zk-chat mcp verify[/] - Verify all servers
    • [cyan]zk-chat mcp verify figma[/] - Verify specific server
    """
    console_gateway = ctx.obj["console_gateway"]
    service = MCPService(ctx.obj["global_config_gateway"])

    if name:
        server = service.get_server(name)
        if not server:
            console_gateway.print(f"[red]❌ Error:[/] MCP server '{name}' not found.")
            raise typer.Exit(1)

        console_gateway.print(f"[dim]Verifying {name} server...[/]")
        if service.verify_server(server):
            console_gateway.print(f"[green]✅ Server '{name}' is available[/]")
        else:
            console_gateway.print(f"[red]❌ Server '{name}' is not available[/]")
            raise typer.Exit(1)
    else:
        servers = service.list_servers()
        if not servers:
            console_gateway.print("[yellow]No MCP servers registered.[/]")
            return

        console_gateway.print(f"[dim]Verifying {len(servers)} server(s)...[/]\n")

        all_available = True
        for server in servers:
            is_available = service.verify_server(server)
            status = "[green]✅[/]" if is_available else "[red]❌[/]"
            console_gateway.print(f"{status} {server.name} ({server.server_type.value})")
            if not is_available:
                all_available = False

        if all_available:
            console_gateway.print("\n[green]✅ All servers are available[/]")
        else:
            console_gateway.print("\n[yellow]⚠️  Some servers are unavailable[/]")
            raise typer.Exit(1)
