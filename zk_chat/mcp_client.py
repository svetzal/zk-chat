"""
MCP Client functionality for connecting to and verifying MCP servers.

This module provides functionality for zk-chat to act as a client
to external MCP servers.
"""

import structlog

from zk_chat.global_config import GlobalConfig, MCPServerConfig, MCPServerType

logger = structlog.get_logger()


def verify_stdio_server(server_config: MCPServerConfig) -> bool:
    """
    Verify that a STDIO MCP server is available.

    Parameters
    ----------
    server_config : MCPServerConfig
        Configuration for the STDIO server

    Returns
    -------
    bool
        True if the server command is available, False otherwise
    """
    if server_config.server_type != MCPServerType.STDIO:
        return False

    try:
        import shutil
        command_path = shutil.which(server_config.command)
        if command_path:
            logger.info("STDIO server command found",
                        server_name=server_config.name,
                        command=server_config.command,
                        path=command_path)
            return True
        else:
            logger.warning("STDIO server command not found",
                           server_name=server_config.name,
                           command=server_config.command)
            return False
    except Exception as e:
        logger.error("Error verifying STDIO server",
                     server_name=server_config.name,
                     error=str(e))
        return False


def verify_http_server(server_config: MCPServerConfig) -> bool:
    """
    Verify that an HTTP MCP server is available.

    Parameters
    ----------
    server_config : MCPServerConfig
        Configuration for the HTTP server

    Returns
    -------
    bool
        True if the server is reachable, False otherwise
    """
    if server_config.server_type != MCPServerType.HTTP:
        return False

    try:
        import requests
        response = requests.get(server_config.url, timeout=5)
        if response.status_code == 200:
            logger.info("HTTP server is reachable",
                        server_name=server_config.name,
                        url=server_config.url)
            return True
        else:
            logger.warning("HTTP server returned non-200 status",
                           server_name=server_config.name,
                           url=server_config.url,
                           status_code=response.status_code)
            return False
    except requests.exceptions.RequestException as e:
        logger.warning("HTTP server is not reachable",
                       server_name=server_config.name,
                       url=server_config.url,
                       error=str(e))
        return False
    except Exception as e:
        logger.error("Error verifying HTTP server",
                     server_name=server_config.name,
                     error=str(e))
        return False


def verify_mcp_server(server_config: MCPServerConfig) -> bool:
    """
    Verify that an MCP server is available.

    Parameters
    ----------
    server_config : MCPServerConfig
        Configuration for the MCP server

    Returns
    -------
    bool
        True if the server is available, False otherwise
    """
    if server_config.server_type == MCPServerType.STDIO:
        return verify_stdio_server(server_config)
    elif server_config.server_type == MCPServerType.HTTP:
        return verify_http_server(server_config)
    else:
        logger.error("Unknown server type",
                     server_name=server_config.name,
                     server_type=server_config.server_type)
        return False


def verify_all_mcp_servers() -> list[str]:
    """
    Verify all registered MCP servers and return list of unavailable servers.

    Returns
    -------
    List[str]
        List of names of unavailable servers (empty if all are available)
    """
    global_config = GlobalConfig.load()
    servers = global_config.list_mcp_servers()

    unavailable = []
    for server in servers:
        if not verify_mcp_server(server):
            unavailable.append(server.name)
            logger.warning("MCP server unavailable", server_name=server.name)
        else:
            logger.info("MCP server available", server_name=server.name)

    return unavailable
