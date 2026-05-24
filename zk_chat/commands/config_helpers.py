from pathlib import Path

import typer

from zk_chat.config import Config
from zk_chat.config_gateway import ConfigGateway
from zk_chat.console_gateway import ConsoleGateway
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.vault_resolution import VaultResolutionError, resolve_vault_path


def load_config_or_exit(vault_path: str, config_gateway: ConfigGateway, console_gateway: ConsoleGateway) -> Config:
    config = config_gateway.load(vault_path)
    if not config:
        console_gateway.print("[yellow]⚠️  Warning:[/] No zk-chat configuration found in vault.")
        console_gateway.print(f"[dim]Run [cyan]zk-chat interactive --vault {vault_path}[/dim] to initialize.")
        raise typer.Exit(1)
    return config


def resolve_vault_or_exit(
    vault: Path | None,
    global_config_gateway: GlobalConfigGateway,
    console_gateway: ConsoleGateway,
    command_hint: str,
) -> str:
    try:
        return resolve_vault_path(vault, global_config_gateway)
    except VaultResolutionError as e:
        console_gateway.print(f"[red]❌ Error:[/] {e}")
        console_gateway.print(f"[yellow]Use:[/] [cyan]{command_hint}[/]")
        raise typer.Exit(1) from e


def resolve_vault_and_load_config(
    vault: Path | None,
    global_config_gateway: GlobalConfigGateway,
    config_gateway: ConfigGateway,
    console_gateway: ConsoleGateway,
    command_hint: str,
) -> tuple[str, Config]:
    vault_path = resolve_vault_or_exit(vault, global_config_gateway, console_gateway, command_hint)
    config = load_config_or_exit(vault_path, config_gateway, console_gateway)
    return vault_path, config


def show_help_if_no_subcommand(ctx: typer.Context, *tip_lines: str) -> None:
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        console = ctx.obj["console_gateway"]
        console.print(ctx.get_help())
        for line in tip_lines:
            console.print(line)
