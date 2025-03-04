import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class ReadZkDocument(LLMTool):
    def __init__(self, zk: Zettelkasten):
        self.zk = zk

    def run(self, relative_path: str) -> str:
        print("Reading document at", relative_path)
        if not self.zk.document_exists(relative_path):
            return f"Document not found at {relative_path}"

        document = self.zk.read_document(relative_path)
        return document.model_dump_json()

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "read_document",
                "description": "Read document content from a file in the Zettelkasten.",
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
