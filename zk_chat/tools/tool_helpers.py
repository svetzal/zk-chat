import json

from pydantic import BaseModel

from zk_chat.services.document_service import DocumentService


def build_descriptor(
    name: str,
    description: str,
    properties: dict | None = None,
    required: list[str] | None = None,
    additional_properties: bool | None = None,
) -> dict:
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
    return json.dumps([r.model_dump(mode="json") for r in results])


def check_document_exists(document_service: DocumentService, relative_path: str) -> str | None:
    if not document_service.document_exists(relative_path):
        return f"Document not found at {relative_path}"
    return None
