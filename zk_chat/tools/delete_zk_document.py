import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_service import RichConsoleService
from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class DeleteZkDocument(LLMTool):
    def __init__(self, zk: Zettelkasten, console_service: RichConsoleService = None):
        self.zk = zk
        self.console_service = console_service or RichConsoleService()

    def run(self, relative_path: str) -> str:
        self.console_service.print(f"[tool.info]Deleting document at {relative_path}[/]")
        if not self.zk.document_exists(relative_path):
            return f"Document not found at {relative_path}"

        try:
            self.zk.delete_document(relative_path)
            return f"Document successfully deleted at {relative_path}"
        except Exception as e:
            logger.error("Error deleting document", path=relative_path, error=str(e))
            return f"Error deleting document at {relative_path}: {str(e)}"

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "delete_document",
                "description": "Permanently delete a document from the Zettelkasten knowledge base. This operation cannot be undone. Use with extreme caution.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_path": {
                            "type": "string",
                            "description": "The relative path within the Zettelkasten of the document to delete."
                        }
                    },
                    "required": ["relative_path"]
                },
            },
        }