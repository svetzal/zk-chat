# ruff: noqa: E402  # Configure logging/env before imports to reduce noisy logs and disable telemetry
import argparse
import logging
import os

# Disable ChromaDB telemetry to avoid PostHog compatibility issues
os.environ['CHROMA_TELEMETRY'] = 'false'

from zk_chat.upgraders.gateway_specific_index_folder import GatewaySpecificIndexFolder
from zk_chat.upgraders.gateway_specific_last_indexed import GatewaySpecificLastIndexed

logging.basicConfig(level=logging.WARN)

from importlib.metadata import version

from mojentic.llm.gateways import OllamaGateway, OpenAIGateway

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import Config, ModelGateway
from zk_chat.console_service import RichConsoleService
from zk_chat.global_config import GlobalConfig
from zk_chat.index import reindex
from zk_chat.memory.smart_memory import SmartMemory


def get_version():
    """Get the package version from metadata."""
    try:
        return version("zk-chat")
    except Exception:
        # Fallback version if package metadata is not available
        return "0.0.0"


def display_banner(config, title: str, unsafe=False, use_git=False, store_prompt=True):
    """Display a colorful banner with application information."""
    console_service = RichConsoleService()
    console = console_service.get_console()

    # Display the banner
    console.print(f"\n[banner.title]{title} v{get_version()}[/]")
    console.print("[banner.copyright]Copyright (C) 2024-2025 Stacey Vetzal[/]\n")

    # Display configuration information
    console.print(
        f"[banner.info.label]Using gateway:[/] [banner.info.value]{config.gateway.value}[/]")
    console.print(f"[banner.info.label]Chat model:[/] [banner.info.value]{config.model}[/]")

    if config.visual_model:
        console.print(
            f"[banner.info.label]Visual Model:[/] [banner.info.value]{config.visual_model}[/]")

    console.print(f"[banner.info.label]Using vault:[/] [banner.info.value]{config.vault}[/]\n")

    # Display warnings based on unsafe and git parameters
    if unsafe:
        if not use_git:
            console.print(
                "[banner.warning.unsafe]ZkChat can write files to your vault, we strongly "
                "recommend using the --git option when using --unsafe.[/]\n")
        else:
            console.print(
                "[banner.warning.git]ZkChat can write files to your vault, and will use git to "
                "provide a full change history and rollback functions.[/]\n")

    # Display information about store_prompt
    if store_prompt:
        console.print(
            "[banner.info.label]System prompt will be stored as 'ZkSystemPrompt.md' in the vault. "
            "Edit this document to help tune your ZkChat experience in this particular vault.[/]\n")


def add_common_args(parser: argparse.ArgumentParser):
    parser.add_argument('--vault', required=False,
                        help='Path to your Zettelkasten vault (can be relative)')
    parser.add_argument('--save', action='store_true',
                        help='Save the provided vault path as a bookmark')
    parser.add_argument('--remove-bookmark', metavar='PATH',
                        help='Remove a bookmark for PATH (can be relative)')
    parser.add_argument('--list-bookmarks', action='store_true', help='List all bookmarks')
    parser.add_argument('--reindex', action='store_true', help='Reindex the Zettelkasten vault')
    parser.add_argument('--full', action='store_true',
                        help='Force full reindex (only with --reindex)')
    parser.add_argument('--gateway', choices=['ollama', 'openai'], default=None,
                        help='Set the model gateway to use (ollama or openai). OpenAI requires '
                             'OPENAI_API_KEY environment variable')
    parser.add_argument('--model', nargs='?', const="choose",
                        help='Set the model to use for chat. Use without a value to select from '
                             'available models')
    parser.add_argument('--visual-model', nargs='?', const="choose",
                        help='Set the model to use for visual analysis. Use without a value to '
                             'select from available models')
    parser.add_argument('--reset-memory', action='store_true', help='Reset the smart memory')


def _handle_save(args, global_config: GlobalConfig) -> bool:
    """Handle --save option. Returns True if the command should exit early."""
    if not args.save:
        return False
    if not args.vault:
        print("Error: --save requires --vault to be specified.")
        return True
    path = args.vault
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.")
        return True
    abs_path = os.path.abspath(path)
    global_config.add_bookmark(abs_path)
    global_config.set_last_opened_bookmark(abs_path)
    print(f"Bookmark added for '{abs_path}'.")
    return True


def _handle_remove_bookmark(args, global_config: GlobalConfig) -> bool:
    """Handle --remove-bookmark. Returns True if handled and should exit."""
    if not args.remove_bookmark:
        return False
    path = args.remove_bookmark
    abs_path = os.path.abspath(path)
    if global_config.remove_bookmark(abs_path):
        print(f"Bookmark for '{abs_path}' removed.")
    else:
        print(f"Error: Bookmark for '{abs_path}' not found.")
    return True


def _handle_list_bookmarks(global_config: GlobalConfig, should_list: bool) -> bool:
    """Handle --list-bookmarks. Returns True if listed and should exit."""
    if not should_list:
        return False
    if not global_config.bookmarks:
        print("No bookmarks found.")
    else:
        print("Bookmarks:")
        for path in global_config.bookmarks:
            last_opened = " (last opened)" if path == global_config.last_opened_bookmark else ""
            print(f"  {path}{last_opened}")
    return True


def _handle_admin_commands(args, global_config: GlobalConfig) -> bool:
    """Process save/remove/list commands. Returns True if handled and should exit."""
    return (
        _handle_save(args, global_config)
        or _handle_remove_bookmark(args, global_config)
        or _handle_list_bookmarks(global_config, getattr(args, "list_bookmarks", False))
    )


def _resolve_vault_path(args, global_config: GlobalConfig) -> str | None:
    """Resolve the vault path from args or bookmarks and ensure it exists."""
    if args.vault:
        vault_path = os.path.abspath(args.vault)
        if vault_path in global_config.bookmarks:
            global_config.set_last_opened_bookmark(vault_path)
            print(f"Using bookmarked vault: {vault_path}")
    else:
        vault_path = global_config.get_last_opened_bookmark_path()
        if not vault_path:
            print("Error: No vault specified. Use --vault or set a bookmark first.")
            return None
    if not os.path.exists(vault_path):
        print(f"Error: Vault path '{vault_path}' does not exist.")
        return None
    return vault_path


def _run_upgraders(config: Config) -> None:
    """Run config upgraders if needed."""
    upgraders = [GatewaySpecificIndexFolder(config), GatewaySpecificLastIndexed(config)]
    for upgrader in upgraders:
        if upgrader.should_run():
            upgrader.run()


def _maybe_select_gateway(args, current_gateway: ModelGateway) -> tuple[ModelGateway, bool]:
    """Return (gateway, changed) based on args.gateway with validation."""
    gateway = current_gateway
    changed = False
    if args.gateway:
        new_gateway = ModelGateway(args.gateway)
        if new_gateway == ModelGateway.OPENAI and not os.environ.get("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY environment variable is not set. Cannot use OpenAI gateway.")
            return gateway, changed
        if new_gateway != current_gateway:
            changed = True
        gateway = new_gateway
    return gateway, changed


def _maybe_update_models(args, config: Config, gateway: ModelGateway) -> None:
    """Update chat and visual models based on args."""
    if args.model is not None:
        if args.model == "choose":
            config.update_model(gateway=gateway)
            if not args.visual_model and not getattr(config, "visual_model", None):
                print("Would you like to select a visual model? (y/n): ")
                choice = input().strip().lower()
                if choice == 'y':
                    config.update_model(gateway=gateway, is_visual=True)
        else:
            config.update_model(args.model, gateway=gateway)

    if args.visual_model:
        if args.visual_model == "choose":
            config.update_model(gateway=gateway, is_visual=True)
        else:
            config.update_model(args.visual_model, gateway=gateway, is_visual=True)


def _reset_smart_memory(vault_path: str, config: Config) -> None:
    """Reset SmartMemory for the vault."""
    db_dir = os.path.join(vault_path, ".zk_chat_db")
    chroma_gateway = ChromaGateway(config.gateway, db_dir=db_dir)
    if config.gateway == ModelGateway.OLLAMA:
        gateway = OllamaGateway()
    elif config.gateway == ModelGateway.OPENAI:
        gateway = OpenAIGateway(os.environ.get("OPENAI_API_KEY"))
    else:
        gateway = OllamaGateway()
    memory = SmartMemory(chroma_gateway, gateway)
    memory.reset()
    print("Smart memory has been reset.")



def _initialize_config(vault_path: str, args) -> Config | None:
    """Initialize config for a new vault based on CLI args without prompting unnecessarily."""
    gateway = ModelGateway.OLLAMA
    if args.gateway:
        gateway = ModelGateway(args.gateway)
        if gateway == ModelGateway.OPENAI and not os.environ.get("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY environment variable is not set. Cannot use OpenAI gateway.")
            return None
    if args.model == "choose":
        return Config.load_or_initialize(
            vault_path,
            gateway=gateway,
            model=None,
            visual_model=(args.visual_model if hasattr(args, "visual_model") else None),
        )
    visual_model = (
        args.visual_model
        if hasattr(args, "visual_model") and args.visual_model is not None
        else args.model
    )
    return Config.load_or_initialize(
        vault_path,
        gateway=gateway,
        model=args.model,
        visual_model=visual_model,
    )


def _handle_existing_config(args, vault_path: str, config: Config) -> Config | None:
    """Handle flows when a config already exists for the vault."""
    _run_upgraders(config)
    gateway, changed = _maybe_select_gateway(args, config.gateway)
    if changed or args.model is not None:
        _maybe_update_models(args, config, gateway)
    if args.reset_memory:
        _reset_smart_memory(vault_path, config)
        return None
    if args.reindex:
        reindex(config, force_full=args.full)
    return config


def _handle_new_config(args, vault_path: str) -> Config | None:
    """Initialize a new config and trigger initial reindex."""
    config = _initialize_config(vault_path, args)
    if not config:
        return None
    reindex(config, force_full=True)
    return config


def common_init(args):
    global_config = GlobalConfig.load()

    if _handle_save(args, global_config):
        return

    if _handle_remove_bookmark(args, global_config):
        return

    if _handle_list_bookmarks(global_config, args.list_bookmarks):
        return

    vault_path = _resolve_vault_path(args, global_config)
    if not vault_path:
        return

    config = Config.load(vault_path)
    if config:
        return _handle_existing_config(args, vault_path, config)
    else:
        return _handle_new_config(args, vault_path)


def common_init_typer(args):
    """
    Typer-compatible version of common_init.

    This function provides the same initialization logic but works with
    the new Typer CLI structure instead of argparse.
    """
    # For now, delegate to the existing common_init function
    # In the future, this could be refactored to be more Typer-native
    return common_init(args)
