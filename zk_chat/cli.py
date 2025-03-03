import argparse
import logging

logging.basicConfig(level=logging.WARN)

from zk_chat.chat import chat
from zk_chat.config import Config
from zk_chat.reindex import reindex
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.chroma_gateway import ChromaGateway
from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway


def main():
    parser = argparse.ArgumentParser(description='Zettelkasten Chat Tool')
    parser.add_argument('--reindex', action='store_true', help='Reindex the Zettelkasten vault')
    parser.add_argument('--full', action='store_true', help='Force full reindex (only with --reindex)')
    parser.add_argument('--unsafe', action='store_true', help='Allow write operations in chat mode')
    parser.add_argument('--model', nargs='?', const="choose",
                        help='Set the model to use for chat. Use without a value to select from available models')
    parser.add_argument('--reset-memory', action='store_true', help='Reset the smart memory')
    args = parser.parse_args()

    config = Config.load()
    if config:
        if args.model:
            if args.model == "choose":
                config.update_model()
            else:
                config.update_model(args.model)

        if args.reset_memory:
            chroma_gateway = ChromaGateway()
            embeddings_gateway = EmbeddingsGateway()
            memory = SmartMemory(chroma_gateway, embeddings_gateway)
            memory.reset()
            print("Smart memory has been reset.")
            return

        if args.reindex:
            reindex(config, force_full=args.full)
    else:
        config = Config.load_or_initialize()

    chat(config, unsafe=args.unsafe)


if __name__ == '__main__':
    main()
