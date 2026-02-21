"""
Interactive model selection for CLI usage.

These functions belong in the imperative shell: they call input()/print() and
interact with external gateways to fetch model lists. They are intentionally
not unit-tested because they are thin wrappers around interactive I/O.
"""

import os

from zk_chat.config import ModelGateway


def get_available_models(gateway: ModelGateway = ModelGateway.OLLAMA) -> list[str]:
    """
    Fetch available models from the specified gateway.

    Parameters
    ----------
    gateway : ModelGateway
        The gateway type to query.

    Returns
    -------
    list[str]
        List of available model names, or empty list on error.
    """
    from zk_chat.gateway_factory import create_model_gateway

    if gateway == ModelGateway.OPENAI and not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        return []
    try:
        g = create_model_gateway(gateway)
    except ValueError as e:
        print(f"Error: {e}")
        return []
    return g.get_available_models()


def select_model(gateway: ModelGateway = ModelGateway.OLLAMA, is_visual: bool = False) -> str:
    """
    Interactively prompt the user to select a model from available options.

    Parameters
    ----------
    gateway : ModelGateway
        Gateway to query for available models.
    is_visual : bool
        If True, the prompt describes visual analysis model selection.

    Returns
    -------
    str
        The selected model name.
    """
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
