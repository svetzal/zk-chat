from zk_chat.models import ZkQueryExcerptResult
from zk_chat.tools.query_tool import QueryTool
from zk_chat.tools.tool_helpers import build_descriptor


class FindExcerptsRelatedTo(QueryTool):
    def _query(self, query: str) -> list[ZkQueryExcerptResult]:
        self.console_gateway.tool_info(f"Querying excerpts related to {query}")
        return self.index_service.query_excerpts(query, max_distance=None)

    def _report(self, results: list[ZkQueryExcerptResult]) -> None:
        self.console_gateway.tool_info(f"Found {len(results)} excerpts:")
        for result in results:
            title = result.excerpt.document_title
            distance = result.distance
            self.console_gateway.tool_info(f"  {title} (distance: {distance:.4f})")
            preview = result.excerpt.text[:100].replace("\n", " ")
            self.console_gateway.tool_info(f"    {preview}...")

    @property
    def descriptor(self) -> dict:
        return build_descriptor(
            name="find_excerpts",
            description="Search for specific passages or excerpts within documents in the "
            "Zettelkasten knowledge base that are relevant to a query. This "
            "returns smaller chunks of text (excerpts) rather than entire documents, "
            "which is useful when you need specific information rather than complete documents.",
            properties={"query": {"type": "string", "description": "The search query to find relevant excerpts."}},
            required=["query"],
        )
