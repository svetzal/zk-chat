import argparse
import logging

from zk_chat.config import Config
from zk_chat.reindex import reindex
from zk_chat.chat import chat

logging.basicConfig(level=logging.WARN)

def main():
    parser = argparse.ArgumentParser(description='Zettelkasten Chat and Reindex Tool')
    parser.add_argument('--reindex', action='store_true', help='Reindex the Zettelkasten vault')
    parser.add_argument('--full', action='store_true', help='Force full reindex (only with --reindex)')
    parser.add_argument('--unsafe', action='store_true', help='Allow write operations in chat mode')
    parser.add_argument('--model', nargs='?', const=None, help='Set the model to use for chat. Use without a value to select from available models')
    args = parser.parse_args()

    config = Config.load_or_initialize()
    if args.model:
        config.update_model(args.model)

    if args.reindex:
        reindex(config, force_full=args.full)
    else:
        chat(config, unsafe=args.unsafe)

if __name__ == '__main__':
    main()
