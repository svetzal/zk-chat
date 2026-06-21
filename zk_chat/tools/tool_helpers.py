"""
Utility helpers for LLM tool development.

Boundary policy: every LLM tool's ``run`` method must catch the exceptions its
service/gateway calls can plausibly raise and return a recoverable error string
via ``log_and_return_error``.  Raw exceptions must never propagate to the agent loop.
"""

import json

import structlog
from pydantic import BaseModel

from zk_chat.services.document_service import DocumentService


class GitToolError(Exception):
    """Raised when a git command executed through ``GitGateway`` returns a failure."""


def checked(result: tuple[bool, str], error_prefix: str) -> str:
    """Unwrap a ``(success, payload)`` tuple, raising ``GitToolError`` on failure.

    Parameters
    ----------
    result : tuple[bool, str]
        Return value from a ``GitGateway`` method.
    error_prefix : str
        Human-readable context prepended to the error message on failure.

    Returns
    -------
    str
        The payload string when the command succeeded.

    Raises
    ------
    GitToolError
        If ``success`` is ``False``.
    """
    success, payload = result
    if not success:
        raise GitToolError(f"{error_prefix}: {payload}")
    return payload


def log_and_return_error(logger: structlog.stdlib.BoundLogger, message: str) -> str:
    """Log ``message`` at ERROR level and return it, for inline use in tool ``run`` methods."""
    logger.error(message)
    return message


def build_descriptor(
    name: str,
    description: str,
    properties: dict | None = None,
    required: list[str] | None = None,
    additional_properties: bool | None = None,
) -> dict:
    """Build an OpenAI-style function descriptor dict for use in LLM tool registration."""
    parameters: dict = {
        "type": "object",
        "properties": properties or {},
        "required": required or [],
    }
    if additional_properties is not None:
        parameters["additionalProperties"] = additional_properties
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters,
        },
    }


def format_model_results(results: list[BaseModel]) -> str:
    """Serialise a list of Pydantic models to a JSON string for returning from LLM tools."""
    return json.dumps([r.model_dump(mode="json") for r in results])


def check_document_exists(document_service: DocumentService, relative_path: str) -> str | None:
    """Return an error message string if the document does not exist, or ``None`` if it does."""
    if not document_service.document_exists(relative_path):
        return f"Document not found at {relative_path}"
    return None
