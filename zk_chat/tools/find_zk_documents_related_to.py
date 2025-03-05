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
        results = self.zk.query_excerpts(query)
        documents = [
            {"id": result.excerpt.document_id, "title": result.excerpt.document_title}
            for result in results
            if result.excerpt.document_id is not None
        ]
        # Remove duplicates while preserving order
        seen = set()
        unique_documents = [
            doc for doc in documents
            if not (doc["id"] in seen or seen.add(doc["id"]))
        ]
        return json.dumps(unique_documents)

    @property
    def descriptor(self):
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
