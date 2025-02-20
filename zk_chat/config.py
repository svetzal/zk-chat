import os
from datetime import datetime
from typing import List, Optional

import requests
from pydantic import BaseModel


def get_available_models() -> List[str]:
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            return [model['name'] for model in response.json()['models']]
        return []
    except:
        return []


def select_model() -> str:
    models = get_available_models()
    if not models:
        return input("No models found in Ollama. Please enter model name manually: ")

    print("\nAvailable models:")
    for idx, model in enumerate(models, 1):
        print(f"{idx}. {model}")

    while True:
        try:
            choice = int(input("\nSelect a model (enter number): "))
            if 1 <= choice <= len(models):
                return models[choice - 1]
        except ValueError:
            pass
        print("Invalid selection. Please try again.")


config_filename: str = os.path.expanduser("~/.zk_chat")


class Config(BaseModel):
    vault: str
    model: str
    chunk_size: int = 500
    chunk_overlap: int = 100
    last_indexed: Optional[datetime] = None

    @classmethod
    def load(cls) -> Optional['Config']:
        if os.path.exists(config_filename):
            with open(config_filename, 'r') as f:
                return cls.model_validate_json(f.read())
        else:
            return None

    @classmethod
    def load_or_initialize(cls) -> 'Config':
        config = cls.load()
        if config:
            return config

        vault = input("Enter path to your zettelkasten vault: ")
        model = select_model()
        config = cls(vault=vault, model=model)
        config.save()
        return config

    def save(self) -> None:
        with open(config_filename, 'w') as f:
            f.write(self.model_dump_json(indent=2))

    def update_model(self, model_name: str = None) -> None:
        """Update the model in config. If model_name is None, interactive selection will be used."""
        if model_name:
            available_models = get_available_models()
            if model_name in available_models:
                self.model = model_name
            else:
                print(f"Model '{model_name}' not found in available models.")
                self.model = select_model()
        else:
            self.model = select_model()

        print("Model selected:", self.model)
        self.save()
