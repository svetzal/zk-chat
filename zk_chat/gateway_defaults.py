"""Default gateway construction for composition roots.

These factory functions centralize the creation of gateway instances
so that CLI commands, GUI entry points, and agents all share one
construction decision. If a gateway ever needs constructor parameters
(e.g. a custom config path), only this file needs to change.
"""

import os

from mojentic.llm.gateways import OllamaGateway, OpenAIGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import Config, ModelGateway
from zk_chat.config_gateway import ConfigGateway
from zk_chat.console_service import ConsoleGateway
from zk_chat.gateway_factory import create_model_gateway
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.tools.git_gateway import GitGateway


def create_default_global_config_gateway() -> GlobalConfigGateway:
    """Create a GlobalConfigGateway with default settings."""
    return GlobalConfigGateway()


def create_default_config_gateway() -> ConfigGateway:
    """Create a ConfigGateway with default settings."""
    return ConfigGateway()


def create_default_console_gateway() -> ConsoleGateway:
    """Create a ConsoleGateway with default settings."""
    return ConsoleGateway()


def create_default_model_gateway(gateway_type: ModelGateway) -> OllamaGateway | OpenAIGateway:
    """Create the appropriate LLM model gateway for the given gateway type."""
    return create_model_gateway(gateway_type)


def create_default_chroma_gateway(config: Config) -> ChromaGateway:
    """Create a ChromaGateway pointed at the standard DB directory for the vault."""
    db_dir = os.path.join(config.vault, ".zk_chat_db")
    return ChromaGateway(config.gateway, db_dir=db_dir)


def create_default_filesystem_gateway(vault: str) -> MarkdownFilesystemGateway:
    """Create a MarkdownFilesystemGateway for the given vault path."""
    return MarkdownFilesystemGateway(vault)


def create_default_tokenizer_gateway() -> TokenizerGateway:
    """Create a TokenizerGateway with default settings."""
    return TokenizerGateway()


def create_default_git_gateway(vault: str) -> GitGateway:
    """Create a GitGateway for the given vault path."""
    return GitGateway(vault)
