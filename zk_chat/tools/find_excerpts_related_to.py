import json
from typing import List

import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.models import ZkQueryResult
from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class FindExcerptsRelatedTo(LLMTool):
    def __init__(self, zk: Zettelkasten):
        self.zk = zk

    def run(self, query: str) -> str:
        print("Querying excerpts related to ", query)
        results: List[ZkQueryResult] = self.zk.query_excerpts(query)
        return json.dumps([
            result.model_dump()
            for result in results
        ])

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "find_excerpts",
                "description": "Find relevant excerpts from the Zettelkasten related to a query.",
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
