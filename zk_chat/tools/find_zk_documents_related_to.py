from zk_chat.models import ZkQueryDocumentResult
from zk_chat.tools.query_tool import QueryTool
from zk_chat.tools.tool_helpers import build_descriptor


class FindZkDocumentsRelatedTo(QueryTool):
    """LLM tool that retrieves semantically similar whole documents from the index."""

    def _query(self, query: str) -> list[ZkQueryDocumentResult]:
        """Query the document index and return ranked ``ZkQueryDocumentResult`` objects."""
        self.console_gateway.tool_info(f"Querying documents related to {query}")
        return self.index_service.query_documents(query)

    def _report(self, results: list[ZkQueryDocumentResult]) -> None:
        """Emit a tool-info summary of each document result including title and distance."""
        self.console_gateway.tool_info(f"Found {len(results)} documents related to the query:")
        for result in results:
            self.console_gateway.tool_info(f"  {result.document.title} (distance: {result.distance:.4f})")

    @property
    def descriptor(self) -> dict:
        """Return the OpenAI-style function descriptor for the ``find_documents`` tool."""
        return build_descriptor(
            name="find_documents",
            description="Search for complete documents in the Zettelkasten knowledge base "
            "that are relevant to a query. This returns entire documents "
            "rather than specific excerpts, which is useful when you need comprehensive "
            "information on a topic rather than just specific passages.",
            properties={"query": {"type": "string", "description": "The search query to find relevant documents."}},
            required=["query"],
        )
