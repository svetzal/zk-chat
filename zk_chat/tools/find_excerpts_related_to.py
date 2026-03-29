import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_service import RichConsoleService
from zk_chat.models import ZkQueryExcerptResult
from zk_chat.services.index_service import IndexService
from zk_chat.tools.tool_helpers import format_model_results

logger = structlog.get_logger()


class FindExcerptsRelatedTo(LLMTool):
    def __init__(self, index_service: IndexService, console_service: RichConsoleService):
        self.index_service = index_service
        self.console_service = console_service

    def run(self, query: str) -> str:
        self.console_service.print(f"[tool.info]Querying excerpts related to {query}[/]")
        results: list[ZkQueryExcerptResult] = self.index_service.query_excerpts(query, max_distance=200.0)
        self.console_service.print(f"[tool.info]Found {len(results)} excerpts:[/]")
        for result in results:
            title = result.excerpt.document_title
            distance = result.distance
            self.console_service.print(f"  [tool.info]{title} (distance: {distance:.4f})[/]")
            preview = result.excerpt.text[:100].replace("\n", " ")
            self.console_service.print(f"    [tool.info]{preview}...[/]")
        return format_model_results(results)

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "find_excerpts",
                "description": "Search for specific passages or excerpts within documents in the "
                "Zettelkasten knowledge base that are relevant to a query. This "
                "returns smaller chunks of text (excerpts) rather than entire documents, "
                "which is useful when you need specific information rather than complete documents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query to find relevant excerpts."}
                    },
                    "required": ["query"],
                },
            },
        }
