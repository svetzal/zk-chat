from unittest.mock import Mock

import pytest
from mojentic.llm import LLMBroker
from mojentic.llm.gateways import OllamaGateway
from mojentic.llm.gateways.models import LLMMessage, MessageRole

from zk_chat.agent import _create_agent
from zk_chat.config import Config, ModelGateway
from zk_chat.global_config import GlobalConfig
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.iterative_problem_solving_agent import IterativeProblemSolvingAgent
from zk_chat.mcp_tool_wrapper import MCPClientManager
from zk_chat.services.service_provider import ServiceProvider
from zk_chat.services.service_registry import ServiceRegistry, ServiceType


@pytest.fixture
def config():
    return Config(vault="/test/vault", model="llama2", gateway=ModelGateway.OLLAMA)


def _response(content: str) -> LLMMessage:
    return LLMMessage(role=MessageRole.Assistant, content=content)


def _make_real_mcp_manager():
    mock_global_config_gateway = Mock(spec=GlobalConfigGateway)
    mock_global_config_gateway.load.return_value = GlobalConfig()
    return MCPClientManager(mock_global_config_gateway)


def _make_real_provider(llm=None):
    registry = ServiceRegistry()
    if llm is None:
        llm = LLMBroker(model="test-model", gateway=Mock(spec=OllamaGateway))
    registry.register_service(ServiceType.LLM_BROKER, llm)
    return ServiceProvider(registry)


class DescribeCreateAgent:
    def should_yield_an_iterative_problem_solving_agent(self, config):
        provider = _make_real_provider()

        with _create_agent(
            config,
            _registry_factory=lambda c: ServiceRegistry(),
            _provider_factory=lambda r: provider,
            _mcp_manager=_make_real_mcp_manager(),
            _system_prompt="agent prompt text",
        ) as solver:
            assert isinstance(solver, IterativeProblemSolvingAgent)

    def should_extend_tools_with_mcp_tools(self, config):
        captured_tools = {}
        provider = _make_real_provider()

        def capture_agent(**kwargs):
            captured_tools["available_tools"] = kwargs["available_tools"]
            return IterativeProblemSolvingAgent(**kwargs)

        with _create_agent(
            config,
            _registry_factory=lambda c: ServiceRegistry(),
            _provider_factory=lambda r: provider,
            _agent_factory=capture_agent,
            _mcp_manager=_make_real_mcp_manager(),
            _system_prompt="agent prompt text",
        ):
            pass

        assert isinstance(captured_tools["available_tools"], list)

    def should_pass_agent_prompt_text_to_agent(self, config):
        captured_kwargs = {}
        provider = _make_real_provider()

        def capture_agent(**kwargs):
            captured_kwargs.update(kwargs)
            return IterativeProblemSolvingAgent(**kwargs)

        with _create_agent(
            config,
            _registry_factory=lambda c: ServiceRegistry(),
            _provider_factory=lambda r: provider,
            _agent_factory=capture_agent,
            _mcp_manager=_make_real_mcp_manager(),
            _system_prompt="the system prompt",
        ):
            pass

        assert captured_kwargs["system_prompt"] == "the system prompt"


class DescribeAgentSingleQuery:
    def should_return_result_of_solver_solve(self, config):
        mock_gateway = Mock(spec=OllamaGateway)
        mock_gateway.complete.side_effect = [
            _response("DONE"),
            _response("the answer"),
        ]
        registry = ServiceRegistry()
        registry.register_service(ServiceType.LLM_BROKER, LLMBroker(model="test-model", gateway=mock_gateway))
        provider = ServiceProvider(registry)

        with _create_agent(
            config,
            _registry_factory=lambda c: ServiceRegistry(),
            _provider_factory=lambda r: provider,
            _mcp_manager=_make_real_mcp_manager(),
            _system_prompt="agent prompt text",
        ) as solver:
            result = solver.solve("what is the meaning of life?")

        assert result == "the answer"

    def should_call_solve_with_the_provided_query(self, config):
        mock_gateway = Mock(spec=OllamaGateway)
        mock_gateway.complete.side_effect = [
            _response("DONE"),
            _response("response"),
        ]
        registry = ServiceRegistry()
        registry.register_service(ServiceType.LLM_BROKER, LLMBroker(model="test-model", gateway=mock_gateway))
        provider = ServiceProvider(registry)
        test_query = "explain zettelkasten"

        with _create_agent(
            config,
            _registry_factory=lambda c: ServiceRegistry(),
            _provider_factory=lambda r: provider,
            _mcp_manager=_make_real_mcp_manager(),
            _system_prompt="agent prompt text",
        ) as solver:
            solver.solve(test_query)

        all_messages = [m for call in mock_gateway.complete.call_args_list for m in call.kwargs.get("messages", [])]
        assert any(test_query in m.content for m in all_messages)
