import structlog
import yaml
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_gateway import ConsoleGateway
from zk_chat.services.document_service import DocumentService
from zk_chat.tools.tool_helpers import build_descriptor, log_and_return_error

logger = structlog.get_logger()


class ListZkDocuments(LLMTool):
    """LLM tool that lists all document paths in the Zettelkasten vault."""

    def __init__(self, document_service: DocumentService, console_gateway: ConsoleGateway) -> None:
        """Store the document service and console gateway used to enumerate documents."""
        self.document_service = document_service
        self.console_gateway = console_gateway

    def run(self) -> str:
        """
        List all document paths in the Zettelkasten.

        Returns:
            A simple list of all document paths.
        """
        self.console_gateway.tool_info("Listing all available documents")
        try:
            paths = [document.relative_path for document in self.document_service.iterate_documents()]
            logger.info("Listed all available documents", paths=paths)
            return "\n".join(paths)
        except (OSError, yaml.YAMLError) as e:
            return log_and_return_error(logger, f"Error listing documents: {str(e)}")

    @property
    def descriptor(self) -> dict:
        """Return the OpenAI-style function descriptor for the ``list_documents`` tool."""
        return build_descriptor(
            name="list_documents",
            description="List all document paths in the Zettelkasten knowledge base. Use "
            "this when you need to see what documents are available in the "
            "system before searching or reading specific documents. This provides an overview of "
            "the available knowledge without retrieving the actual content.",
        )
