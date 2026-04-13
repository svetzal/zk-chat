"""Default gateway construction for composition roots.

These factory functions centralize the creation of gateway instances
so that CLI commands, GUI entry points, and agents all share one
construction decision. If a gateway ever needs constructor parameters
(e.g. a custom config path), only this file needs to change.
"""

from zk_chat.config_gateway import ConfigGateway
from zk_chat.console_service import ConsoleGateway
from zk_chat.global_config_gateway import GlobalConfigGateway


def create_default_global_config_gateway() -> GlobalConfigGateway:
    """Create a GlobalConfigGateway with default settings."""
    return GlobalConfigGateway()


def create_default_config_gateway() -> ConfigGateway:
    """Create a ConfigGateway with default settings."""
    return ConfigGateway()


def create_default_console_gateway() -> ConsoleGateway:
    """Create a ConsoleGateway with default settings."""
    return ConsoleGateway()
