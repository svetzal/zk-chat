import json

import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class ListZkDocuments(LLMTool):
    def __init__(self, zk: Zettelkasten):
        self.zk = zk

    def run(self) -> str:
        """
        List all document paths in the Zettelkasten.
        
        Returns:
            A simple list of all document paths.
        """
        print("Listing all available documents")
        paths = [document.relative_path for document in self.zk.iterate_documents()]
        logger.info("Listed all available documents", paths=paths)
        return "\n".join(paths)

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "list_documents",
                "description": "List all document titles in the Zettelkasten.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
            },
        }