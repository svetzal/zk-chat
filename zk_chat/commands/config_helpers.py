import typer

from zk_chat.config import Config
from zk_chat.config_gateway import ConfigGateway
from zk_chat.console_gateway import ConsoleGateway


def load_config_or_exit(vault_path: str, config_gateway: ConfigGateway, console_gateway: ConsoleGateway) -> Config:
    config = config_gateway.load(vault_path)
    if not config:
        console_gateway.print("[yellow]⚠️  Warning:[/] No zk-chat configuration found in vault.")
        console_gateway.print(f"[dim]Run [cyan]zk-chat interactive --vault {vault_path}[/dim] to initialize.")
        raise typer.Exit(1)
    return config
