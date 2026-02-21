import json

import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_service import RichConsoleService
from zk_chat.models import ZkQueryDocumentResult
from zk_chat.services.index_service import IndexService

logger = structlog.get_logger()


class FindZkDocumentsRelatedTo(LLMTool):
    def __init__(self, index_service: IndexService, console_service: RichConsoleService = None):
        self.index_service = index_service
        self.console_service = console_service or RichConsoleService()

    def run(self, query: str) -> str:
        self.console_service.print(f"[tool.info]Querying documents related to {query}[/]")
        document_results: list[ZkQueryDocumentResult] = self.index_service.query_documents(query)
        self.console_service.print(f"[tool.info]Found {len(document_results)} documents related to the query:[/]")
        for result in document_results:
            self.console_service.print(f"  [tool.info]{result.document.title} (distance: {result.distance:.4f})[/]")
        return json.dumps(
            [
                document.model_dump(mode="json")  # mode json to handle datetime serialization
                for document in document_results
            ]
        )

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "find_documents",
                "description": "Search for complete documents in the Zettelkasten knowledge base "
                "that are relevant to a query. This returns entire documents "
                "rather than specific excerpts, which is useful when you need comprehensive "
                "information on a topic rather than just specific passages.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query to find relevant documents."}
                    },
                    "required": ["query"],
                },
            },
        }
