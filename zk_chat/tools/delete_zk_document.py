import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_gateway import ConsoleGateway
from zk_chat.services.document_service import DocumentService
from zk_chat.services.index_service import IndexService
from zk_chat.tools.tool_helpers import build_descriptor, check_document_exists, tool_boundary

logger = structlog.get_logger()


class DeleteZkDocument(LLMTool):
    """LLM tool that permanently deletes a document from the vault and removes it from the index."""

    def __init__(
        self, document_service: DocumentService, index_service: IndexService, console_gateway: ConsoleGateway
    ) -> None:
        """Store the services needed to delete a document from both the filesystem and index."""
        self.document_service = document_service
        self.index_service = index_service
        self.console_gateway = console_gateway

    @tool_boundary(
        (FileNotFoundError, OSError),
        lambda self, relative_path: f"Error deleting document at {relative_path}",
    )
    def run(self, relative_path: str) -> str:
        """Delete the document at ``relative_path`` from the vault and its index entry."""
        self.console_gateway.tool_info(f"Deleting document at {relative_path}")
        error = check_document_exists(self.document_service, relative_path)
        if error:
            return error

        self.document_service.delete_document(relative_path)
        self.index_service.remove_document_from_index(relative_path)
        return f"Document successfully deleted at {relative_path}"

    @property
    def descriptor(self) -> dict:
        """Return the OpenAI-style function descriptor for the ``delete_document`` tool."""
        return build_descriptor(
            name="delete_document",
            description="Permanently delete a document from the Zettelkasten knowledge "
            "base. This operation cannot be undone. Use with extreme caution.",
            properties={
                "relative_path": {
                    "type": "string",
                    "description": "The relative path within the Zettelkasten of the document to delete.",
                }
            },
            required=["relative_path"],
        )
