from abc import abstractmethod

from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_gateway import ConsoleGateway
from zk_chat.services.index_service import IndexService
from zk_chat.tools.tool_helpers import format_model_results, tool_boundary


class QueryTool(LLMTool):
    """Base for tools that query the index and return JSON-serialized results."""

    def __init__(self, index_service: IndexService, console_gateway: ConsoleGateway) -> None:
        """Store the index service and console gateway for use by subclass implementations."""
        self.index_service = index_service
        self.console_gateway = console_gateway

    @tool_boundary(Exception, "Error querying the index")
    def run(self, query: str) -> str:
        """Execute the query, emit console feedback, and return JSON-serialized results."""
        results = self._query(query)
        self._report(results)
        return format_model_results(results)

    @abstractmethod
    def _query(self, query: str) -> list:
        """Execute the index query and return result models."""

    @abstractmethod
    def _report(self, results: list) -> None:
        """Emit console feedback describing the results."""
