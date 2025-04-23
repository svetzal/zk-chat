import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class ReadZkDocument(LLMTool):

    zk: Zettelkasten

    def __init__(self, zk: Zettelkasten):
        self.zk = zk

    def run(self, relative_path: str) -> str:
        logger.info("Reading document", relative_path=relative_path)
        if not self.zk.document_exists(relative_path):
            return f"Document not found at {relative_path}"

        document = self.zk.read_document(relative_path)
        return document.model_dump_json()

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "read_document",
                "description": "Retrieve and read the full content of a specific document from the Zettelkasten knowledge base. Use this when you need to access the complete content of a document that you already know exists (for example, after using list_documents or find_documents). This returns the entire document including its metadata and content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_path": {
                            "type": "string",
                            "description": "The relative path within the Zettelkasten from which to read the file."
                        }
                    },
                    "required": ["relative_path"]
                },
            },
        }
