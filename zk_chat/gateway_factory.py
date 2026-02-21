"""Factory for creating model gateways based on configuration."""

import os

from mojentic.llm.gateways import OllamaGateway, OpenAIGateway

from zk_chat.config import ModelGateway


def create_model_gateway(gateway: ModelGateway) -> OllamaGateway | OpenAIGateway:
    """Create the appropriate LLM gateway based on the configured gateway type.

    Parameters
    ----------
    gateway : ModelGateway
        The gateway type to create (OLLAMA or OPENAI).

    Returns
    -------
    OllamaGateway | OpenAIGateway
        The configured gateway instance.

    Raises
    ------
    ValueError
        If the gateway type is not recognized.
    """
    match gateway:
        case ModelGateway.OLLAMA:
            return OllamaGateway()
        case ModelGateway.OPENAI:
            return OpenAIGateway(os.environ.get("OPENAI_API_KEY"))
        case _:
            raise ValueError(f"Unsupported gateway type: {gateway}")
