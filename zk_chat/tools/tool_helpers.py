"""
Utility helpers for LLM tool development.

Boundary policy: ``tool_boundary`` is the canonical idiom for every LLM tool's ``run``
method — catch exceptions the service/gateway calls can plausibly raise and return a
recoverable error string.  ``checked()`` is its complement for git ``(success, payload)``
tuple-returns.  Domain "not found" / expected-result returns (e.g. ``ResolveWikiLink``)
are explicitly out of scope: they represent valid control flow, not backend-failure guards,
and must not use this decorator.
"""

import functools
import json

import structlog
from pydantic import BaseModel

from zk_chat.services.document_service import DocumentService

_logger = structlog.get_logger()

PASSTHROUGH = object()
"""Sentinel for the ``tool_boundary`` mapping form: return ``str(e)`` unchanged, without logging."""


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


def _tool_boundary_mapping(mapping):
    """Build a ``tool_boundary`` decorator from an ``{ExceptionType: prefix}`` mapping."""
    exception_tuple = tuple(mapping.keys())

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except exception_tuple as e:
                for exc_cls, exc_prefix in mapping.items():
                    if isinstance(e, exc_cls):
                        if exc_prefix is PASSTHROUGH:
                            return str(e)
                        p = exc_prefix(*args, **kwargs) if callable(exc_prefix) else exc_prefix
                        return log_and_return_error(_logger, f"{p}: {e}")
                return log_and_return_error(_logger, str(e))
        return wrapper
    return decorator


def tool_boundary(exception_types_or_mapping, prefix=None):
    """Decorator for LLM tool ``run`` methods that catches exceptions and returns error strings.

    Accepts two call signatures:

    **Simple form** (single exception type or tuple)::

        @tool_boundary(OSError, "Error writing document")
        def run(self, ...):
            ...

    **Mapping form** (per-type handling, supports ``PASSTHROUGH`` sentinel)::

        @tool_boundary({GitToolError: PASSTHROUGH, OSError: "Unexpected error"})
        def run(self, ...):
            ...

    Parameters
    ----------
    exception_types_or_mapping : type | tuple[type, ...] | dict
        Exception types to catch.  When a dict, keys are exception types and values are
        string prefixes, callables, or the ``PASSTHROUGH`` sentinel (return ``str(e)``
        unchanged without logging).
    prefix : str | callable | None
        Used only in the simple form.  Static string, or a callable with the same signature
        as the decorated method that returns the context-specific prefix at runtime.
    """
    if isinstance(exception_types_or_mapping, dict):
        return _tool_boundary_mapping(exception_types_or_mapping)

    exception_types = exception_types_or_mapping

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except exception_types as e:
                p = prefix(*args, **kwargs) if callable(prefix) else prefix
                return log_and_return_error(_logger, f"{p}: {e}")
        return wrapper
    return decorator
