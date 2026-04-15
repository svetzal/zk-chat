from typing import Any

import structlog
import yaml
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_service import ConsoleGateway
from zk_chat.filename_utils import ensure_md_extension, sanitize_filename
from zk_chat.models import ZkDocument
from zk_chat.services.document_service import DocumentService

logger = structlog.get_logger()


def prepare_document(title: str, content: str, metadata: dict[str, Any] | None = None) -> ZkDocument:
    """Prepare a ZkDocument from raw inputs.

    Sanitizes the title for use as a filename, ensures the .md extension, and
    augments metadata with ``{"reviewed": False}``.

    Parameters
    ----------
    title : str
        Document title (will be sanitized for use as filename).
    content : str
        Document body content.
    metadata : dict[str, Any] | None
        Optional metadata dictionary. Non-dict values are treated as absent.

    Returns
    -------
    ZkDocument
        Ready-to-write document instance.
    """
    relative_path = ensure_md_extension(sanitize_filename(title))
    base_metadata = {} if metadata is None or not isinstance(metadata, dict) else metadata
    augmented_metadata = base_metadata | {"reviewed": False}
    return ZkDocument(relative_path=relative_path, metadata=augmented_metadata, content=content)


class CreateOrOverwriteZkDocument(LLMTool):
    def __init__(self, document_service: DocumentService, console_service: ConsoleGateway) -> None:
        self.document_service = document_service
        self.console_service = console_service

    def run(self, title: str, content: str, metadata: dict[str, Any] | None = None) -> str:
        document = prepare_document(title, content, metadata)
        self.console_service.print(f"[tool.info]Writing document at {document.relative_path}[/]")
        try:
            logger.info("writing file", relative_path=document.relative_path, metadata=document.metadata)
            self.document_service.write_document(document)
            return f"Successfully wrote to {document.relative_path}\n{document.model_dump_json()}"
        except OSError as e:
            error_message = (
                f"Failed to write document to {document.relative_path}: {str(e)}. This could "
                f"be due to insufficient permissions, disk space issues, "
                f"or the directory being read-only."
            )
            logger.error(error_message)
            return error_message
        except yaml.YAMLError as e:
            error_message = (
                f"Failed to serialize metadata for document {document.relative_path}: {str(e)}. Please check if "
                f"the metadata contains valid YAML content."
            )
            logger.error(error_message)
            return error_message

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "create_or_overwrite_document",
                "description": "Create a new document or update an existing document in the Zettelkasten knowledge "
                "base. Use this when you need to add new information to the knowledge base or update "
                "existing information. This tool will create a new document if the title doesn't "
                "exist, or completely replace the content of an existing document. Returns a success "
                "message with the document details if successful, or an error message if the operation "
                "fails.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "The title of the document"},
                        "content": {
                            "type": "string",
                            "description": "The body content for the document. DO NOT INCLUDE FRONT-MATTER OR TITLE. "
                            "Content should be in markdown format, with proper unescaped newline "
                            "characters",
                        },
                        "metadata": {
                            "type": "object",
                            "description": "The metadata for the document in JSON format. If not provided, "
                            "the metadata will be empty.",
                            "optional": True,
                        },
                    },
                    "additionalProperties": False,
                    "required": ["title", "content"],
                },
            },
        }
