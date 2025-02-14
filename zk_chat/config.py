import configparser
import os

CONFIG_PATH = os.path.expanduser("~/.zk_chat")


def load_or_initialize_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_PATH):
        config.read(CONFIG_PATH)
        vault = config.get('zk_chat', 'vault')
        model = config.get('zk_chat', 'model')
    else:
        vault = input("Enter path to your zettelkasten vault: ")
        model = input("Enter LLM model to use: ")
        config['zk_chat'] = {'vault': vault, 'model': model}
        with open(CONFIG_PATH, 'w') as f:
            config.write(f)
    return vault, model
