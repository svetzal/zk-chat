import argparse
import os
from importlib.metadata import version

import zk_chat.bootstrap  # noqa: F401  # Sets CHROMA_TELEMETRY and logging before chromadb imports
from zk_chat.config import Config, ModelGateway
from zk_chat.config_gateway import ConfigGateway
from zk_chat.config_resolution import (
    determine_init_config_action,
    determine_model_action,
    determine_model_update_action,
    resolve_vault_from_args,
    validate_gateway_selection,
)
from zk_chat.console_service import RichConsoleService
from zk_chat.global_config import GlobalConfig
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.index import reindex
from zk_chat.model_selection import get_available_models, select_model
from zk_chat.service_factory import build_service_registry
from zk_chat.services.service_provider import ServiceProvider
from zk_chat.upgraders.gateway_specific_index_folder import GatewaySpecificIndexFolder
from zk_chat.upgraders.gateway_specific_last_indexed import GatewaySpecificLastIndexed


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
    console.print(f"[banner.info.label]Using gateway:[/] [banner.info.value]{config.gateway.value}[/]")
    console.print(f"[banner.info.label]Chat model:[/] [banner.info.value]{config.model}[/]")

    if config.visual_model:
        console.print(f"[banner.info.label]Visual Model:[/] [banner.info.value]{config.visual_model}[/]")

    console.print(f"[banner.info.label]Using vault:[/] [banner.info.value]{config.vault}[/]\n")

    # Display warnings based on unsafe and git parameters
    if unsafe:
        if not use_git:
            console.print(
                "[banner.warning.unsafe]ZkChat can write files to your vault, we strongly "
                "recommend using the --git option when using --unsafe.[/]\n"
            )
        else:
            console.print(
                "[banner.warning.git]ZkChat can write files to your vault, and will use git to "
                "provide a full change history and rollback functions.[/]\n"
            )

    # Display information about store_prompt
    if store_prompt:
        console.print(
            "[banner.info.label]System prompt will be stored as 'ZkSystemPrompt.md' in the vault. "
            "Edit this document to help tune your ZkChat experience in this particular vault.[/]\n"
        )


def add_common_args(parser: argparse.ArgumentParser):
    parser.add_argument("--vault", required=False, help="Path to your Zettelkasten vault (can be relative)")
    parser.add_argument("--save", action="store_true", help="Save the provided vault path as a bookmark")
    parser.add_argument("--remove-bookmark", metavar="PATH", help="Remove a bookmark for PATH (can be relative)")
    parser.add_argument("--list-bookmarks", action="store_true", help="List all bookmarks")
    parser.add_argument("--reindex", action="store_true", help="Reindex the Zettelkasten vault")
    parser.add_argument("--full", action="store_true", help="Force full reindex (only with --reindex)")
    parser.add_argument(
        "--gateway",
        choices=["ollama", "openai"],
        default=None,
        help="Set the model gateway to use (ollama or openai). OpenAI requires OPENAI_API_KEY environment variable",
    )
    parser.add_argument(
        "--model",
        nargs="?",
        const="choose",
        help="Set the model to use for chat. Use without a value to select from available models",
    )
    parser.add_argument(
        "--visual-model",
        nargs="?",
        const="choose",
        help="Set the model to use for visual analysis. Use without a value to select from available models",
    )
    parser.add_argument("--reset-memory", action="store_true", help="Reset the smart memory")


def _handle_save(args, global_config: GlobalConfig, global_config_gateway: GlobalConfigGateway) -> bool:
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
    global_config_gateway.save(global_config)
    print(f"Bookmark added for '{abs_path}'.")
    return True


def _handle_remove_bookmark(args, global_config: GlobalConfig, global_config_gateway: GlobalConfigGateway) -> bool:
    """Handle --remove-bookmark. Returns True if handled and should exit."""
    if not args.remove_bookmark:
        return False
    path = args.remove_bookmark
    abs_path = os.path.abspath(path)
    if global_config.remove_bookmark(abs_path):
        global_config_gateway.save(global_config)
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


def _handle_admin_commands(args, global_config: GlobalConfig, global_config_gateway: GlobalConfigGateway) -> bool:
    """Process save/remove/list commands. Returns True if handled and should exit."""
    return (
        _handle_save(args, global_config, global_config_gateway)
        or _handle_remove_bookmark(args, global_config, global_config_gateway)
        or _handle_list_bookmarks(global_config, getattr(args, "list_bookmarks", False))
    )


def _resolve_vault_path(args, global_config: GlobalConfig, global_config_gateway: GlobalConfigGateway) -> str | None:
    """Resolve the vault path from args or bookmarks and ensure it exists."""
    arg_vault = os.path.abspath(args.vault) if args.vault else None
    result = resolve_vault_from_args(
        arg_vault=arg_vault,
        bookmarks=global_config.bookmarks,
        last_opened=global_config.get_last_opened_bookmark_path(),
    )
    if result.error:
        print(f"Error: {result.error}")
        return None
    vault_path = result.vault_path
    if result.source == "argument" and vault_path in global_config.bookmarks:
        global_config.set_last_opened_bookmark(vault_path)
        global_config_gateway.save(global_config)
        print(f"Using bookmarked vault: {vault_path}")
    if not os.path.exists(vault_path):
        print(f"Error: Vault path '{vault_path}' does not exist.")
        return None
    return vault_path


def _run_upgraders(config: Config, config_gateway: ConfigGateway) -> None:
    """Run config upgraders if needed."""
    upgraders = [
        GatewaySpecificIndexFolder(config),
        GatewaySpecificLastIndexed(config, config_gateway),
    ]
    for upgrader in upgraders:
        if upgrader.should_run():
            upgrader.run()


def _maybe_select_gateway(args, current_gateway: ModelGateway) -> tuple[ModelGateway, bool]:
    """Return (gateway, changed) based on args.gateway with validation."""
    result = validate_gateway_selection(
        requested=args.gateway,
        current_gateway=current_gateway,
        openai_key_present=bool(os.environ.get("OPENAI_API_KEY")),
    )
    if result.error:
        print(f"Error: {result.error}")
    return result.gateway, result.changed


def _update_model_in_config(config: Config, model_name: str | None, gateway: ModelGateway, is_visual: bool) -> None:
    """Update a single model field on config using interactive selection if needed."""
    available_models = get_available_models(gateway)
    action = determine_model_action(model_name, available_models)
    if action.error:
        print(action.error)
    if action.needs_interactive_selection:
        selected = select_model(gateway, is_visual=is_visual)
    else:
        selected = action.model_name
    if is_visual:
        config.visual_model = selected
    else:
        config.model = selected

    model_type = "Visual model" if is_visual else "Chat model"
    current_name = config.visual_model if is_visual else config.model
    print(f"{model_type} selected: {current_name} (using {gateway.value} gateway)")


def _maybe_update_models(args, config: Config, gateway: ModelGateway, config_gateway: ConfigGateway) -> None:
    """Update chat and visual models based on args."""
    action = determine_model_update_action(
        model_arg=args.model,
        visual_model_arg=args.visual_model,
        has_existing_visual_model=bool(getattr(config, "visual_model", None)),
    )

    if action.update_chat_model:
        _update_model_in_config(config, action.chat_model_name, gateway, is_visual=False)

    if action.prompt_for_visual_model:
        print("Would you like to select a visual model? (y/n): ")
        choice = input().strip().lower()
        if choice == "y":
            _update_model_in_config(config, None, gateway, is_visual=True)

    if action.update_visual_model:
        _update_model_in_config(config, action.visual_model_name, gateway, is_visual=True)

    config_gateway.save(config)


def _reset_smart_memory(vault_path: str, config: Config) -> None:
    """Reset SmartMemory for the vault."""
    registry = build_service_registry(config)
    provider = ServiceProvider(registry)
    memory = provider.get_smart_memory()
    memory.reset()
    print("Smart memory has been reset.")


def _initialize_config(vault_path: str, args, config_gateway: ConfigGateway) -> Config | None:
    """Initialize config for a new vault based on CLI args without prompting unnecessarily."""
    action = determine_init_config_action(
        gateway_arg=args.gateway,
        model_arg=args.model,
        visual_model_arg=args.visual_model if hasattr(args, "visual_model") else None,
        openai_key_present=bool(os.environ.get("OPENAI_API_KEY")),
    )

    if action.error:
        print(action.error)
        return None

    if action.needs_chat_model_selection:
        print("Please select a model for chat:")
        model = select_model(action.gateway)
    else:
        model = action.chat_model_name

    if action.needs_visual_model_selection:
        print("Please select a model for visual analysis:")
        visual_model = select_model(action.gateway, is_visual=True)
    elif action.use_chat_model_for_visual:
        visual_model = model
    elif action.visual_model_name is not None:
        visual_model = action.visual_model_name
    elif action.needs_visual_model_prompt:
        print("Would you like to select a model for visual analysis? (y/n): ")
        choice = input().strip().lower()
        if choice == "y":
            print("Please select a model for visual analysis:")
            visual_model = select_model(action.gateway, is_visual=True)
        else:
            visual_model = None
            print("Visual analysis will be disabled.")
    else:
        visual_model = None

    config = Config(vault=vault_path, model=model, visual_model=visual_model, gateway=action.gateway)
    config_gateway.save(config)
    return config


def _handle_existing_config(args, vault_path: str, config: Config, config_gateway: ConfigGateway) -> Config | None:
    """Handle flows when a config already exists for the vault."""
    _run_upgraders(config, config_gateway)
    gateway, changed = _maybe_select_gateway(args, config.gateway)
    if changed or args.model is not None:
        _maybe_update_models(args, config, gateway, config_gateway)
    if args.reset_memory:
        _reset_smart_memory(vault_path, config)
        return None
    if args.reindex:
        reindex(config, config_gateway, force_full=args.full)
    return config


def _handle_new_config(args, vault_path: str, config_gateway: ConfigGateway) -> Config | None:
    """Initialize a new config and trigger initial reindex."""
    config = _initialize_config(vault_path, args, config_gateway)
    if not config:
        return None
    reindex(config, config_gateway, force_full=True)
    return config


def common_init(args):
    global_config_gateway = GlobalConfigGateway()
    global_config = global_config_gateway.load()
    config_gateway = ConfigGateway()

    if _handle_save(args, global_config, global_config_gateway):
        return

    if _handle_remove_bookmark(args, global_config, global_config_gateway):
        return

    if _handle_list_bookmarks(global_config, args.list_bookmarks):
        return

    vault_path = _resolve_vault_path(args, global_config, global_config_gateway)
    if not vault_path:
        return

    config = config_gateway.load(vault_path)
    if config:
        return _handle_existing_config(args, vault_path, config, config_gateway)
    else:
        return _handle_new_config(args, vault_path, config_gateway)


def common_init_typer(args):
    """
    Typer-compatible version of common_init.

    This function provides the same initialization logic but works with
    the new Typer CLI structure instead of argparse.
    """
    # For now, delegate to the existing common_init function
    # In the future, this could be refactored to be more Typer-native
    return common_init(args)
