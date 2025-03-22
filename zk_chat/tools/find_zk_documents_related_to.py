import json

import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class FindZkDocumentsRelatedTo(LLMTool):
    def __init__(self, zk: Zettelkasten):
        self.zk = zk

    def run(self, query: str) -> str:
        print("Querying documents related to ", query)
        documents = self.zk.query_documents(query)
        return json.dumps([
            document.model_dump()
            for document in documents
        ])

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "find_documents",
                "description": "Find relevant documents from the Zettelkasten related to a query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find relevant documents."
                        }
                    },
                    "required": ["query"]
                },
            },
        }
