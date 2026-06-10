from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any

import structlog

import zk_chat.bootstrap  # noqa: F401  # Sets CHROMA_TELEMETRY and logging before chromadb imports
from zk_chat.config import Config
from zk_chat.console_gateway import ConsoleGateway
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.iterative_problem_solving_agent import IterativeProblemSolvingAgent
from zk_chat.mcp_client import verify_all_mcp_servers
from zk_chat.mcp_tool_wrapper import MCPClientManager
from zk_chat.tool_assembly import build_tools_from_config

logger = structlog.get_logger()


@contextmanager
def _create_agent(
    config: Config,
    _registry_factory: Callable[..., Any] | None = None,
    _provider_factory: Callable[..., Any] | None = None,
    _agent_factory: Callable[..., Any] | None = None,
    _mcp_manager: Any | None = None,
    _system_prompt: str | None = None,
) -> Iterator[IterativeProblemSolvingAgent]:
    """Build a fully-wired IterativeProblemSolvingAgent from config.

    Parameters
    ----------
    config : Config
        Application configuration
    _registry_factory : callable, optional
        Injectable factory for service registry (for testing)
    _provider_factory : callable, optional
        Injectable factory for service provider (for testing)
    _agent_factory : callable, optional
        Injectable factory for the agent (for testing)
    _mcp_manager : context manager, optional
        Injectable MCP client manager (for testing or injection from callers)
    _system_prompt : str, optional
        Injectable system prompt text (for testing)
    """
    agent_factory = _agent_factory or IterativeProblemSolvingAgent

    components = build_tools_from_config(
        config,
        registry_factory=_registry_factory,
        provider_factory=_provider_factory,
        system_prompt=_system_prompt,
    )

    mcp_ctx = _mcp_manager

    with mcp_ctx as mcp_manager:
        tools = list(components.tools)
        tools.extend(mcp_manager.get_tools())

        yield agent_factory(
            llm=components.llm_broker,
            available_tools=tools,
            system_prompt=components.system_prompt,
        )


def agent(
    config: Config,
    global_config_gateway: GlobalConfigGateway,
    mcp_manager: MCPClientManager,
    console_gateway: ConsoleGateway,
) -> None:
    logger.info("Starting interactive agent session", model=config.model, gateway=config.gateway.value)
    global_config = global_config_gateway.load()
    if global_config.list_mcp_servers():
        console_gateway.print("Verifying MCP server availability...")
        unavailable = verify_all_mcp_servers(global_config_gateway)
        if unavailable:
            console_gateway.print("\nWarning: The following MCP servers are unavailable:")
            for name in unavailable:
                console_gateway.print(f"  - {name}")
            console_gateway.print("\nYou can continue, but these servers will not be accessible during the session.")
            console_gateway.print(
                "Use 'zk-chat mcp verify' to check server status or 'zk-chat mcp list' to see all servers.\n"
            )

    with _create_agent(config, _mcp_manager=mcp_manager) as solver:
        while True:
            query = console_gateway.input("Agent request: ")
            if not query:
                break
            else:
                response = solver.solve(query)
                console_gateway.print(response)


def agent_single_query(config: Config, query: str, mcp_manager: MCPClientManager) -> str:
    """
    Execute a single query using the agent and return the response.

    Parameters
    ----------
    config : Config
        Configuration object
    query : str
        The query string to process
    mcp_manager : MCPClientManager
        MCP client manager for loading MCP tool integrations

    Returns
    -------
    str
        The agent's response as a string
    """
    logger.info("Starting single-query agent session", model=config.model, gateway=config.gateway.value)
    with _create_agent(config, _mcp_manager=mcp_manager) as solver:
        return solver.solve(query)
