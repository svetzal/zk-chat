"""
Interactive model selection for CLI usage.

These functions belong in the imperative shell: they call input()/print() and
interact with external gateways to fetch model lists. They are intentionally
not unit-tested because they are thin wrappers around interactive I/O.
"""

import os

from zk_chat.config import ModelGateway
from zk_chat.console_gateway import ConsoleGateway


def get_available_models(
    gateway: ModelGateway = ModelGateway.OLLAMA,
    console_gateway: ConsoleGateway | None = None,
) -> list[str]:
    """
    Fetch available models from the specified gateway.

    Parameters
    ----------
    gateway : ModelGateway
        The gateway type to query.
    console_gateway : ConsoleGateway | None
        Console gateway for output. If None, errors are silently ignored.

    Returns
    -------
    list[str]
        List of available model names, or empty list on error.
    """
    from zk_chat.gateway_factory import create_model_gateway

    if gateway == ModelGateway.OPENAI and not os.environ.get("OPENAI_API_KEY"):
        if console_gateway is not None:
            console_gateway.print("Error: OPENAI_API_KEY environment variable is not set.")
        return []
    try:
        g = create_model_gateway(gateway)
    except ValueError as e:
        if console_gateway is not None:
            console_gateway.print(f"Error: {e}")
        return []
    return g.get_available_models()


def _prompt_input(prompt: str, console_gateway: ConsoleGateway | None) -> str:
    if console_gateway is not None:
        return console_gateway.input(prompt)
    return input(prompt)


def _print_message(message: str, console_gateway: ConsoleGateway | None) -> None:
    if console_gateway is not None:
        console_gateway.print(message)
    else:
        print(message)


def select_model(
    gateway: ModelGateway = ModelGateway.OLLAMA,
    is_visual: bool = False,
    console_gateway: ConsoleGateway | None = None,
) -> str:
    """
    Interactively prompt the user to select a model from available options.

    Parameters
    ----------
    gateway : ModelGateway
        Gateway to query for available models.
    is_visual : bool
        If True, the prompt describes visual analysis model selection.
    console_gateway : ConsoleGateway | None
        Console gateway for interactive I/O. If None, falls back to bare input/print.

    Returns
    -------
    str
        The selected model name.
    """
    model_type = "visual analysis" if is_visual else "chat"
    models = get_available_models(gateway, console_gateway)
    if not models:
        if gateway == ModelGateway.OLLAMA:
            prompt = f"No models found in Ollama. Please enter {model_type} model name manually: "
        else:
            prompt = f"No models available. Please enter {model_type} model name manually: "
        return _prompt_input(prompt, console_gateway)

    _print_message(f"\nAvailable {gateway.value} models for {model_type}:", console_gateway)
    for idx, model in enumerate(models, 1):
        _print_message(f"{idx}. {model}", console_gateway)

    while True:
        try:
            choice_str = _prompt_input(f"\nSelect a {model_type} model (enter number): ", console_gateway)
            choice = int(choice_str)
            if 1 <= choice <= len(models):
                return models[choice - 1]
        except ValueError:
            pass
        _print_message("Invalid selection. Please try again.", console_gateway)
