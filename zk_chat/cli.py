import argparse
import logging
import os

logging.basicConfig(level=logging.WARN)

from zk_chat.chat import chat
from zk_chat.config import Config, ModelGateway
from zk_chat.global_config import GlobalConfig
from zk_chat.reindex import reindex
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.chroma_gateway import ChromaGateway
from mojentic.llm.gateways import OllamaGateway, OpenAIGateway
from zk_chat.tools.git_gateway import GitGateway


def main():
    parser = argparse.ArgumentParser(description='Zettelkasten Chat Tool')
    parser.add_argument('--vault', required=False, help='Path to your Zettelkasten vault (can be relative)')
    parser.add_argument('--save', action='store_true',
                        help='Save the provided vault path as a bookmark')
    parser.add_argument('--remove-bookmark', metavar='PATH', help='Remove a bookmark for PATH (can be relative)')
    parser.add_argument('--list-bookmarks', action='store_true', help='List all bookmarks')
    parser.add_argument('--reindex', action='store_true', help='Reindex the Zettelkasten vault')
    parser.add_argument('--full', action='store_true', help='Force full reindex (only with --reindex)')
    parser.add_argument('--unsafe', action='store_true', help='Allow write operations in chat mode')
    parser.add_argument('--gateway', choices=['ollama', 'openai'], default=None,
                        help='Set the model gateway to use (ollama or openai). OpenAI requires OPENAI_API_KEY environment variable')
    parser.add_argument('--model', nargs='?', const="choose",
                        help='Set the model to use for chat. Use without a value to select from available models')
    parser.add_argument('--visual-model', nargs='?', const="choose",
                        help='Set the model to use for visual analysis. Use without a value to select from available models')
    parser.add_argument('--reset-memory', action='store_true', help='Reset the smart memory')
    parser.add_argument('--git', action='store_true', help='Enable git integration')
    parser.add_argument('--store-prompt', action='store_false', help='Store the system prompt to the vault', dest='store_prompt', default=True)
    args = parser.parse_args()

    global_config = GlobalConfig.load()

    if args.save:
        if not args.vault:
            print("Error: --save requires --vault to be specified.")
            return
        path = args.vault
        if not os.path.exists(path):
            print(f"Error: Path '{path}' does not exist.")
            return
        abs_path = os.path.abspath(path)
        global_config.add_bookmark(abs_path)
        global_config.set_last_opened_bookmark(abs_path)
        print(f"Bookmark added for '{abs_path}'.")

    if args.remove_bookmark:
        path = args.remove_bookmark
        abs_path = os.path.abspath(path)
        if global_config.remove_bookmark(abs_path):
            print(f"Bookmark for '{abs_path}' removed.")
        else:
            print(f"Error: Bookmark for '{abs_path}' not found.")
        return

    if args.list_bookmarks:
        if not global_config.bookmarks:
            print("No bookmarks found.")
        else:
            print("Bookmarks:")
            for path in global_config.bookmarks:
                last_opened = " (last opened)" if path == global_config.last_opened_bookmark else ""
                print(f"  {path}{last_opened}")
        return

    vault_path = None

    if args.vault:
        vault_path = os.path.abspath(args.vault)

        if vault_path in global_config.bookmarks:
            global_config.set_last_opened_bookmark(vault_path)
            print(f"Using bookmarked vault: {vault_path}")

    else:
        vault_path = global_config.get_last_opened_bookmark_path()
        if not vault_path:
            print("Error: No vault specified. Use --vault or set a bookmark first.")
            return
        print(f"Using last-used vault: {vault_path}")

    if not os.path.exists(vault_path):
        print(f"Error: Vault path '{vault_path}' does not exist.")
        return

    config = Config.load(vault_path)
    if config:
        gateway = config.gateway
        gateway_changed = False

        if args.gateway:
            new_gateway = ModelGateway(args.gateway)

            if new_gateway == ModelGateway.OPENAI and not os.environ.get("OPENAI_API_KEY"):
                print("Error: OPENAI_API_KEY environment variable is not set. Cannot use OpenAI gateway.")
                return

            if new_gateway != config.gateway:
                gateway_changed = True

            gateway = new_gateway

        if gateway_changed or args.model:
            if args.model == "choose":
                config.update_model(gateway=gateway)
                # If user chose to select a model and no visual model is specified, also prompt for visual model
                if not args.visual_model and not config.visual_model:
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

        if args.reset_memory:
            db_dir = os.path.join(vault_path, ".zk_chat_db")
            chroma_gateway = ChromaGateway(db_dir=db_dir)

            if config.gateway == ModelGateway.OLLAMA:
                gateway = OllamaGateway()
            elif config.gateway == ModelGateway.OPENAI:
                gateway = OpenAIGateway(os.environ.get("OPENAI_API_KEY"))
            else:
                gateway = OllamaGateway()

            memory = SmartMemory(chroma_gateway, gateway)
            memory.reset()
            print("Smart memory has been reset.")
            return

        if args.reindex:
            reindex(config, force_full=args.full)
    else:
        gateway = ModelGateway.OLLAMA
        if args.gateway:
            gateway = ModelGateway(args.gateway)
            if gateway == ModelGateway.OPENAI and not os.environ.get("OPENAI_API_KEY"):
                print("Error: OPENAI_API_KEY environment variable is not set. Cannot use OpenAI gateway.")
                return

        if args.model == "choose":
            config = Config.load_or_initialize(vault_path, gateway=gateway)
        else:
            config = Config.load_or_initialize(vault_path, gateway=gateway, model=args.model)

        reindex(config, force_full=True)

    if args.git:
        git_gateway = GitGateway(vault_path)
        git_gateway.setup()

    chat(config, unsafe=args.unsafe, use_git=args.git, store_prompt=args.store_prompt)


if __name__ == '__main__':
    main()
