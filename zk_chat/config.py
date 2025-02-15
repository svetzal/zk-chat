import os
import json
import requests
from typing import List
from pydantic import BaseModel

CONFIG_PATH = os.path.expanduser("~/.zk_chat")

class Config(BaseModel):
    vault: str
    model: str
    chunk_size: int = 500
    chunk_overlap: int = 100

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

def load_or_initialize_config() -> Config:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return Config.model_validate_json(f.read())
    
    vault = input("Enter path to your zettelkasten vault: ")
    model = select_model()
    config = Config(vault=vault, model=model)
    
    with open(CONFIG_PATH, 'w') as f:
        f.write(config.model_dump_json())
    
    return config
