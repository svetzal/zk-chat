import json

from pydantic import BaseModel

from zk_chat.services.document_service import DocumentService


def format_model_results(results: list[BaseModel]) -> str:
    return json.dumps([r.model_dump(mode="json") for r in results])


def check_document_exists(document_service: DocumentService, relative_path: str) -> str | None:
    if not document_service.document_exists(relative_path):
        return f"Document not found at {relative_path}"
    return None
