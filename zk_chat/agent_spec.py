from unittest.mock import MagicMock, Mock

import pytest
from mojentic.llm import LLMBroker
from mojentic.llm.gateways import OllamaGateway

from zk_chat.agent import _create_agent
from zk_chat.config import Config, ModelGateway
from zk_chat.iterative_problem_solving_agent import IterativeProblemSolvingAgent
from zk_chat.services.service_registry import ServiceRegistry


@pytest.fixture
def config():
    return Config(vault="/test/vault", model="llama2", gateway=ModelGateway.OLLAMA)


def _make_mcp_manager_context(mcp_tools=None):
    """Build a mock MCPClientManager that behaves as a context manager."""
    mock_manager = MagicMock()
    mock_manager.__enter__ = Mock(return_value=mock_manager)
    mock_manager.__exit__ = Mock(return_value=False)
    mock_manager.get_tools.return_value = mcp_tools or []
    return mock_manager


def _make_mock_provider():
    """Build a mock ServiceProvider with minimal stubs for all services."""
    mock_llm = LLMBroker(model="test-model", gateway=Mock(spec=OllamaGateway))
    mock_provider = Mock()
    mock_provider.get_filesystem_gateway.return_value = None
    mock_provider.get_document_service.return_value = None
    mock_provider.get_index_service.return_value = None
    mock_provider.get_link_traversal_service.return_value = None
    mock_provider.get_llm_broker.return_value = mock_llm
    mock_provider.get_smart_memory.return_value = None
    mock_provider.get_git_gateway.return_value = None
    mock_provider.get_model_gateway.return_value = None
    mock_provider.get_console_service.return_value = None
    return mock_provider


class DescribeCreateAgent:
    def should_yield_an_iterative_problem_solving_agent(self, config):
        mock_agent = Mock(spec=IterativeProblemSolvingAgent)
        mock_provider = _make_mock_provider()

        with _create_agent(
            config,
            _registry_factory=lambda c: ServiceRegistry(),
            _provider_factory=lambda r: mock_provider,
            _agent_factory=lambda **kwargs: mock_agent,
            _mcp_manager=_make_mcp_manager_context(),
            _system_prompt="agent prompt text",
        ) as solver:
            assert solver is mock_agent

    def should_extend_tools_with_mcp_tools(self, config):
        mock_mcp_tool = MagicMock()
        captured_tools = {}
        mock_provider = _make_mock_provider()

        def capture_agent(**kwargs):
            captured_tools["available_tools"] = kwargs["available_tools"]
            return Mock(spec=IterativeProblemSolvingAgent)

        with _create_agent(
            config,
            _registry_factory=lambda c: ServiceRegistry(),
            _provider_factory=lambda r: mock_provider,
            _agent_factory=capture_agent,
            _mcp_manager=_make_mcp_manager_context([mock_mcp_tool]),
            _system_prompt="agent prompt text",
        ):
            pass

        assert mock_mcp_tool in captured_tools["available_tools"]

    def should_pass_agent_prompt_text_to_agent(self, config):
        captured_kwargs = {}
        mock_provider = _make_mock_provider()

        def capture_agent(**kwargs):
            captured_kwargs.update(kwargs)
            return Mock(spec=IterativeProblemSolvingAgent)

        with _create_agent(
            config,
            _registry_factory=lambda c: ServiceRegistry(),
            _provider_factory=lambda r: mock_provider,
            _agent_factory=capture_agent,
            _mcp_manager=_make_mcp_manager_context(),
            _system_prompt="the system prompt",
        ):
            pass

        assert captured_kwargs["system_prompt"] == "the system prompt"


class DescribeAgentSingleQuery:
    def should_return_result_of_solver_solve(self, config):
        mock_agent = Mock(spec=IterativeProblemSolvingAgent)
        mock_agent.solve.return_value = "the answer"
        mock_provider = _make_mock_provider()

        with _create_agent(
            config,
            _registry_factory=lambda c: ServiceRegistry(),
            _provider_factory=lambda r: mock_provider,
            _agent_factory=lambda **kwargs: mock_agent,
            _mcp_manager=_make_mcp_manager_context(),
            _system_prompt="agent prompt text",
        ) as solver:
            result = solver.solve("what is the meaning of life?")

        assert result == "the answer"

    def should_call_solve_with_the_provided_query(self, config):
        mock_agent = Mock(spec=IterativeProblemSolvingAgent)
        mock_agent.solve.return_value = "response"
        mock_provider = _make_mock_provider()
        test_query = "explain zettelkasten"

        with _create_agent(
            config,
            _registry_factory=lambda c: ServiceRegistry(),
            _provider_factory=lambda r: mock_provider,
            _agent_factory=lambda **kwargs: mock_agent,
            _mcp_manager=_make_mcp_manager_context(),
            _system_prompt="agent prompt text",
        ) as solver:
            solver.solve(test_query)

        mock_agent.solve.assert_called_once_with(test_query)
