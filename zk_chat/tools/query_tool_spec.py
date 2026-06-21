import json

import pytest

from zk_chat.tools.conftest import _make_index_service
from zk_chat.tools.query_tool import QueryTool


class ErrorQueryTool(QueryTool):
    def _query(self, query: str) -> list:
        raise RuntimeError("index unavailable")

    def _report(self, results: list) -> None:
        pass

    @property
    def descriptor(self) -> dict:
        return {}


class ConcreteQueryTool(QueryTool):
    def __init__(self, index_service, console_gateway, query_results):
        super().__init__(index_service, console_gateway)
        self._query_results = query_results
        self.reported = []

    def _query(self, query: str) -> list:
        return self._query_results

    def _report(self, results: list) -> None:
        self.reported.extend(results)

    @property
    def descriptor(self) -> dict:
        return {}


@pytest.fixture
def index_service():
    return _make_index_service()


@pytest.fixture
def query_results():
    from pydantic import BaseModel

    class Item(BaseModel):
        label: str

    return [Item(label="a"), Item(label="b")]


@pytest.fixture
def tool(index_service, mock_console_gateway, query_results):
    return ConcreteQueryTool(index_service, mock_console_gateway, query_results)


class DescribeQueryTool:
    """Tests for the QueryTool skeleton: _query → _report → format_model_results."""

    def should_call_report_with_query_results(self, tool, query_results):
        tool.run("test query")

        assert tool.reported == query_results

    def should_return_json_serialized_results(self, tool, query_results):
        result = tool.run("test query")

        parsed = json.loads(result)
        assert len(parsed) == len(query_results)
        assert parsed[0]["label"] == "a"
        assert parsed[1]["label"] == "b"

    def should_store_injected_dependencies(self, index_service, mock_console_gateway, query_results):
        t = ConcreteQueryTool(index_service, mock_console_gateway, query_results)

        assert t.index_service is index_service
        assert t.console_gateway is mock_console_gateway

    def should_return_error_message_when_query_fails(self, index_service, mock_console_gateway):
        tool = ErrorQueryTool(index_service, mock_console_gateway)

        result = tool.run("test query")

        assert "Error querying the index" in result
