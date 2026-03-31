from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from zk_chat.agent import _create_agent, agent_single_query
from zk_chat.config import Config, ModelGateway
from zk_chat.iterative_problem_solving_agent import IterativeProblemSolvingAgent


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


def _make_tracker_patches(mcp_tools=None):
    """Return a dict of all patch targets needed to exercise _create_agent."""
    return {
        "zk_chat.agent.build_service_registry": patch("zk_chat.agent.build_service_registry"),
        "zk_chat.agent.ServiceProvider": patch("zk_chat.agent.ServiceProvider"),
        "zk_chat.agent.build_agent_tools": patch("zk_chat.agent.build_agent_tools", return_value=[]),
        "zk_chat.agent.create_default_global_config_gateway": patch(
            "zk_chat.agent.create_default_global_config_gateway"
        ),
        "zk_chat.agent.MCPClientManager": patch(
            "zk_chat.agent.MCPClientManager", return_value=_make_mcp_manager_context(mcp_tools)
        ),
        "builtins.open": patch("builtins.open", mock_open(read_data="agent prompt text")),
    }


class DescribeCreateAgent:
    def should_yield_an_iterative_problem_solving_agent(self, config):
        mock_agent = Mock(spec=IterativeProblemSolvingAgent)

        with (
            patch("zk_chat.agent.build_service_registry"),
            patch("zk_chat.agent.ServiceProvider"),
            patch("zk_chat.agent.build_agent_tools", return_value=[]),
            patch("zk_chat.agent.create_default_global_config_gateway"),
            patch("zk_chat.agent.MCPClientManager", return_value=_make_mcp_manager_context()),
            patch("builtins.open", mock_open(read_data="agent prompt text")),
            patch("zk_chat.agent.IterativeProblemSolvingAgent", return_value=mock_agent),
        ):
            with _create_agent(config) as solver:
                assert solver is mock_agent

    def should_extend_tools_with_mcp_tools(self, config):
        mock_mcp_tool = MagicMock()
        base_tools = [MagicMock()]
        captured_tools = {}

        def capture_agent(**kwargs):
            captured_tools["available_tools"] = kwargs["available_tools"]
            return Mock(spec=IterativeProblemSolvingAgent)

        with (
            patch("zk_chat.agent.build_service_registry"),
            patch("zk_chat.agent.ServiceProvider"),
            patch("zk_chat.agent.build_agent_tools", return_value=base_tools),
            patch("zk_chat.agent.create_default_global_config_gateway"),
            patch("zk_chat.agent.MCPClientManager", return_value=_make_mcp_manager_context([mock_mcp_tool])),
            patch("builtins.open", mock_open(read_data="agent prompt text")),
            patch("zk_chat.agent.IterativeProblemSolvingAgent", side_effect=capture_agent),
        ):
            with _create_agent(config):
                pass

        assert mock_mcp_tool in captured_tools["available_tools"]

    def should_pass_agent_prompt_text_to_agent(self, config):
        captured_kwargs = {}

        def capture_agent(**kwargs):
            captured_kwargs.update(kwargs)
            return Mock(spec=IterativeProblemSolvingAgent)

        with (
            patch("zk_chat.agent.build_service_registry"),
            patch("zk_chat.agent.ServiceProvider"),
            patch("zk_chat.agent.build_agent_tools", return_value=[]),
            patch("zk_chat.agent.create_default_global_config_gateway"),
            patch("zk_chat.agent.MCPClientManager", return_value=_make_mcp_manager_context()),
            patch("builtins.open", mock_open(read_data="the system prompt")),
            patch("zk_chat.agent.IterativeProblemSolvingAgent", side_effect=capture_agent),
        ):
            with _create_agent(config):
                pass

        assert captured_kwargs["system_prompt"] == "the system prompt"


class DescribeAgentSingleQuery:
    def should_return_result_of_solver_solve(self, config):
        mock_agent = Mock(spec=IterativeProblemSolvingAgent)
        mock_agent.solve.return_value = "the answer"

        with (
            patch("zk_chat.agent.build_service_registry"),
            patch("zk_chat.agent.ServiceProvider"),
            patch("zk_chat.agent.build_agent_tools", return_value=[]),
            patch("zk_chat.agent.create_default_global_config_gateway"),
            patch("zk_chat.agent.MCPClientManager", return_value=_make_mcp_manager_context()),
            patch("builtins.open", mock_open(read_data="agent prompt text")),
            patch("zk_chat.agent.IterativeProblemSolvingAgent", return_value=mock_agent),
        ):
            result = agent_single_query(config, "what is the meaning of life?")

        assert result == "the answer"

    def should_call_solve_with_the_provided_query(self, config):
        mock_agent = Mock(spec=IterativeProblemSolvingAgent)
        mock_agent.solve.return_value = "response"
        test_query = "explain zettelkasten"

        with (
            patch("zk_chat.agent.build_service_registry"),
            patch("zk_chat.agent.ServiceProvider"),
            patch("zk_chat.agent.build_agent_tools", return_value=[]),
            patch("zk_chat.agent.create_default_global_config_gateway"),
            patch("zk_chat.agent.MCPClientManager", return_value=_make_mcp_manager_context()),
            patch("builtins.open", mock_open(read_data="agent prompt text")),
            patch("zk_chat.agent.IterativeProblemSolvingAgent", return_value=mock_agent),
        ):
            agent_single_query(config, test_query)

        mock_agent.solve.assert_called_once_with(test_query)
