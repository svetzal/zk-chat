import json
from typing import List

import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.models import ZkQueryExcerptResult
from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class FindExcerptsRelatedTo(LLMTool):
    def __init__(self, zk: Zettelkasten):
        self.zk = zk

    def run(self, query: str) -> str:
        print("Querying excerpts related to ", query)
        results: List[ZkQueryExcerptResult] = self.zk.query_excerpts(query)
        return json.dumps([
            result.model_dump()
            for result in results
        ])

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "find_excerpts",
                "description": "Search for specific passages or excerpts within documents in the Zettelkasten knowledge base that are relevant to a query. This returns smaller chunks of text (excerpts) rather than entire documents, which is useful when you need specific information rather than complete documents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find relevant excerpts."
                        }
                    },
                    "required": ["query"]
                },
            },
        }
