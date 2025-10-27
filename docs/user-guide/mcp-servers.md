# MCP Servers

Model Context Protocol (MCP) servers extend Zk-Chat with external tools and capabilities.

## What is MCP?

MCP (Model Context Protocol) is a standard for connecting AI applications to external tools and data sources. Zk-Chat can integrate with MCP servers to provide additional capabilities beyond its built-in tools.

## Managing MCP Servers

### Add a Server

#### STDIO Server

For servers that communicate via standard input/output:

```bash
zk-chat mcp add server-name --type stdio --command server-command
```

Example:

```bash
zk-chat mcp add figma --type stdio --command figma-mcp
```

#### HTTP Server

For servers that expose an HTTP API:

```bash
zk-chat mcp add server-name --type http --url http://localhost:8080
```

Example:

```bash
zk-chat mcp add chrome --type http --url http://localhost:8080
```

### List Servers

View all registered MCP servers:

```bash
zk-chat mcp list
```

### Verify Server Availability

Check if servers are available:

```bash
# Verify all servers
zk-chat mcp verify

# Verify specific server
zk-chat mcp verify server-name
```

### Remove a Server

```bash
zk-chat mcp remove server-name
```

## Using MCP Servers

MCP servers are automatically verified before chat or agent sessions start. If a server is unavailable, you'll see a warning, but you can continue with the session.

The tools provided by MCP servers are automatically available to the AI during chat sessions.

## Example MCP Servers

### Figma MCP Server

Access Figma designs and data:

```bash
zk-chat mcp add figma --type stdio --command figma-mcp
```

### Custom MCP Servers

You can create your own MCP servers following the MCP specification. See the [MCP documentation](https://modelcontextprotocol.io/) for details.

## Next Steps

- [Visual Analysis](visual-analysis.md) - Image analysis capabilities
- [Smart Memory](smart-memory.md) - Persistent context storage
- [Plugin Development](../plugins/overview.md) - Create Zk-Chat plugins
