import os
from datetime import datetime
from enum import Enum
from typing import List, Optional

import requests
from mojentic.llm.gateways import OllamaGateway, OpenAIGateway
from pydantic import BaseModel


class ModelGateway(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"


def get_available_models(gateway: ModelGateway = ModelGateway.OLLAMA) -> List[str]:
    if gateway == ModelGateway.OLLAMA:
        g = OllamaGateway()
    elif gateway == ModelGateway.OPENAI:
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            print("Error: OPENAI_API_KEY environment variable is not set.")
            return []
        g = OpenAIGateway(openai_key)
    return g.get_available_models()


def select_model(gateway: ModelGateway = ModelGateway.OLLAMA, is_visual: bool = False) -> str:
    model_type = "visual analysis" if is_visual else "chat"
    models = get_available_models(gateway)
    if not models:
        if gateway == ModelGateway.OLLAMA:
            return input(f"No models found in Ollama. Please enter {model_type} model name manually: ")
        else:
            return input(f"No models available. Please enter {model_type} model name manually: ")

    print(f"\nAvailable {gateway.value} models for {model_type}:")
    for idx, model in enumerate(models, 1):
        print(f"{idx}. {model}")

    while True:
        try:
            choice = int(input(f"\nSelect a {model_type} model (enter number): "))
            if 1 <= choice <= len(models):
                return models[choice - 1]
        except ValueError:
            pass
        print("Invalid selection. Please try again.")


def get_config_path(vault_path: str) -> str:
    """Get the path to the config file in the vault directory."""
    return os.path.join(vault_path, ".zk_chat")


class Config(BaseModel):
    vault: str
    model: str  # Chat model
    visual_model: Optional[str] = None  # Visual analysis model
    gateway: ModelGateway = ModelGateway.OLLAMA
    chunk_size: int = 500
    chunk_overlap: int = 100
    last_indexed: Optional[datetime] = None

    @classmethod
    def load(cls, vault_path: str) -> Optional['Config']:
        config_path = get_config_path(vault_path)
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return cls.model_validate_json(f.read())
        else:
            return None

    @classmethod
    def load_or_initialize(cls, vault_path: str, gateway: ModelGateway = ModelGateway.OLLAMA, model: str = None, visual_model: str = None) -> 'Config':
        config = cls.load(vault_path)
        if config:
            # If config exists, just return it - visual_model can be None
            return config

        # Initialize new config
        if model is None:
            print("Please select a model for chat:")
            model = select_model(gateway)

        if visual_model is None:
            print("Would you like to select a model for visual analysis? (y/n): ")
            choice = input().strip().lower()
            if choice == 'y':
                print("Please select a model for visual analysis:")
                visual_model = select_model(gateway, is_visual=True)
            else:
                visual_model = None
                print("Visual analysis will be disabled.")

        config = cls(vault=vault_path, model=model, visual_model=visual_model, gateway=gateway)

        config.save()
        return config

    def save(self) -> None:
        config_path = get_config_path(self.vault)
        with open(config_path, 'w') as f:
            f.write(self.model_dump_json(indent=2))

    def update_model(self, model_name: str = None, gateway: ModelGateway = None, is_visual: bool = False) -> None:
        """
        Update the model in config. If model_name is None, interactive selection will be used.

        Args:
            model_name: Name of the model to use
            gateway: Gateway to use
            is_visual: If True, update the visual model instead of the chat model
        """
        # Update gateway if specified
        if gateway is not None:
            self.gateway = gateway

        if model_name:
            available_models = get_available_models(self.gateway)
            if model_name in available_models:
                if is_visual:
                    self.visual_model = model_name
                else:
                    self.model = model_name
            else:
                print(f"Model '{model_name}' not found in available models.")
                selected_model = select_model(self.gateway)
                if is_visual:
                    self.visual_model = selected_model
                else:
                    self.model = selected_model
        else:
            selected_model = select_model(self.gateway)
            if is_visual:
                self.visual_model = selected_model
            else:
                self.model = selected_model

        model_type = "Visual model" if is_visual else "Chat model"
        model_name = self.visual_model if is_visual else self.model
        print(f"{model_type} selected: {model_name} (using {self.gateway.value} gateway)")
        self.save()
