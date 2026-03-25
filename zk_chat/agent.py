from contextlib import contextmanager
from pathlib import Path

import zk_chat.bootstrap  # noqa: F401  # Sets CHROMA_TELEMETRY and logging before chromadb imports
from zk_chat.config import Config
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.iterative_problem_solving_agent import IterativeProblemSolvingAgent
from zk_chat.mcp_client import verify_all_mcp_servers
from zk_chat.mcp_tool_wrapper import MCPClientManager
from zk_chat.service_factory import build_service_registry
from zk_chat.services.service_provider import ServiceProvider
from zk_chat.tool_assembly import build_agent_tools


def _get_global_config_gateway() -> GlobalConfigGateway:
    return GlobalConfigGateway()


@contextmanager
def _create_agent(config: Config):
    """Build a fully-wired IterativeProblemSolvingAgent from config."""
    registry = build_service_registry(config)
    provider = ServiceProvider(registry)

    tools = build_agent_tools(
        config=config,
        filesystem_gateway=provider.get_filesystem_gateway(),
        document_service=provider.get_document_service(),
        index_service=provider.get_index_service(),
        link_traversal_service=provider.get_link_traversal_service(),
        llm=provider.get_llm_broker(),
        smart_memory=provider.get_smart_memory(),
        git_gateway=provider.get_git_gateway(),
        gateway=provider.get_model_gateway(),
        console_service=provider.get_console_service(),
    )

    with MCPClientManager(_get_global_config_gateway()) as mcp_manager:
        tools.extend(mcp_manager.get_tools())

        agent_prompt_path = Path(__file__).parent / "agent_prompt.txt"
        with open(agent_prompt_path) as f:
            agent_prompt = f.read()

        yield IterativeProblemSolvingAgent(
            llm=provider.get_llm_broker(),
            available_tools=tools,
            system_prompt=agent_prompt,
        )


def agent(config: Config):
    global_config_gateway = _get_global_config_gateway()
    global_config = global_config_gateway.load()
    if global_config.list_mcp_servers():
        print("Verifying MCP server availability...")
        unavailable = verify_all_mcp_servers(global_config_gateway)
        if unavailable:
            print("\nWarning: The following MCP servers are unavailable:")
            for name in unavailable:
                print(f"  - {name}")
            print("\nYou can continue, but these servers will not be accessible during the session.")
            print("Use 'zk-chat mcp verify' to check server status or 'zk-chat mcp list' to see all servers.\n")

    with _create_agent(config) as solver:
        while True:
            query = input("Agent request: ")
            if not query:
                break
            else:
                response = solver.solve(query)
                print(response)


def agent_single_query(config: Config, query: str) -> str:
    """
    Execute a single query using the agent and return the response.

    Parameters
    ----------
    config : Config
        Configuration object
    query : str
        The query string to process

    Returns
    -------
    str
        The agent's response as a string
    """
    with _create_agent(config) as solver:
        return solver.solve(query)
