# MCP Servers

Model Context Protocol (MCP) servers extend zk-chat with external tools and capabilities.

## What is MCP?

The Model Context Protocol (MCP) is a standardized way for AI applications to connect to external tools and data sources. MCP servers can:

- Provide additional tools and capabilities
- Run independently of zk-chat
- Be implemented in any programming language
- Integrate with various external systems

## MCP vs zk-chat Plugins

### zk-chat Plugins

**Advantages:**
- Deep integration with zk-chat runtime
- Access to vault, database, and memory
- Faster execution (no IPC overhead)
- Simple Python development

**When to use:**
- Tools that need vault access
- Tools requiring Smart Memory
- Python-based tools
- Performance-critical operations

### MCP Servers

**Advantages:**
- Language agnostic
- Process isolation
- Independent deployment
- Cross-platform compatibility
- Usable by multiple AI systems

**When to use:**
- Non-Python implementations
- Tools that need isolation
- Resource-intensive operations
- Cross-system compatibility

See [Plugin Development Guide](../plugins/guide.md) for plugin details.

## Managing MCP Servers

### Adding Servers

#### STDIO Servers

For command-line tools:

```bash
zk-chat mcp add figma --type stdio --command figma-mcp
```

With arguments:

```bash
zk-chat mcp add custom --type stdio --command my-server --args "--port 8080"
```

#### HTTP Servers

For web-based tools:

```bash
zk-chat mcp add chrome --type http --url http://localhost:9222
```

### Listing Servers

View all registered servers:

```bash
zk-chat mcp list
```

Output shows:
- Server name
- Type (STDIO/HTTP)
- Configuration
- Status

### Verifying Servers

Check if servers are available:

```bash
# Verify all servers
zk-chat mcp verify

# Verify specific server
zk-chat mcp verify figma
```

### Removing Servers

Remove a registered server:

```bash
zk-chat mcp remove figma
```

## Using MCP Servers

### Automatic Integration

MCP servers are automatically:
- Verified before chat sessions
- Integrated with available tools
- Made available to the AI

### In Chat Sessions

The AI can use MCP server tools like any other tool:

```
You: Use Figma to create a wireframe

AI: Using tool: create_figma_wireframe
[MCP server executes tool]

Wireframe created successfully
```

### Server Availability

If a server is unavailable:

```bash
$ zk-chat interactive

Warning: MCP server 'figma' is unavailable
Would you like to continue anyway? (y/n):
```

You can:
- Continue without the server
- Fix the server issue
- Remove the server configuration

## Example MCP Servers

### Browser Automation

```bash
# Chrome DevTools Protocol
zk-chat mcp add chrome --type http --url http://localhost:9222
```

Use for:
- Web scraping
- Screenshot capture
- Browser automation

### Design Tools

```bash
# Figma integration
zk-chat mcp add figma --type stdio --command figma-mcp
```

Use for:
- Creating designs
- Exporting assets
- Design collaboration

### Development Tools

```bash
# GitHub integration
zk-chat mcp add github --type stdio --command github-mcp
```

Use for:
- Repository operations
- Issue management
- PR reviews

### Database Access

```bash
# Database query server
zk-chat mcp add database --type http --url http://localhost:8080
```

Use for:
- Data queries
- Report generation
- Analytics

## Configuration Storage

MCP server configurations are stored in:

```
~/.config/zk-chat/mcp_servers.json
```

The file contains server definitions:

```json
{
  "servers": {
    "figma": {
      "type": "stdio",
      "command": "figma-mcp",
      "args": []
    },
    "chrome": {
      "type": "http",
      "url": "http://localhost:9222"
    }
  }
}
```

## Developing MCP Servers

### MCP Server Requirements

An MCP server must:
- Implement the MCP protocol
- Provide tool definitions
- Handle tool execution requests
- Return results in MCP format

### MCP Protocol

The protocol defines:
- **Tool Discovery** - List available tools
- **Tool Execution** - Execute tools with parameters
- **Result Format** - Standardized response format

### Example Server (Node.js)

```javascript
const { McpServer } = require('@modelcontextprotocol/sdk');

const server = new McpServer({
  name: 'example-server',
  version: '1.0.0',
});

server.tool('example_tool', 
  {
    description: 'An example tool',
    parameters: {
      input: { type: 'string', description: 'Input text' }
    }
  },
  async (params) => {
    // Tool implementation
    return { result: `Processed: ${params.input}` };
  }
);

server.start();
```

### Languages and SDKs

MCP servers can be implemented in:
- **Python** - Official SDK available
- **Node.js** - Official SDK available
- **TypeScript** - Official SDK available
- **Any language** - Implement protocol manually

## Best Practices

### Server Naming

Use descriptive names:
```bash
# Good
zk-chat mcp add github-api
zk-chat mcp add chrome-devtools

# Less clear
zk-chat mcp add server1
zk-chat mcp add tool
```

### Server Health Checks

Verify servers regularly:
```bash
# Before important sessions
zk-chat mcp verify
```

### Documentation

Document custom servers:
- What tools they provide
- How to install/start them
- Configuration requirements
- Usage examples

### Error Handling

MCP servers should:
- Provide clear error messages
- Handle failures gracefully
- Timeout appropriately
- Log issues for debugging

## Troubleshooting

### Server Not Found

**Error:** "MCP server 'name' not found"

**Check:**
```bash
# Verify server is registered
zk-chat mcp list

# Add if missing
zk-chat mcp add name --type stdio --command cmd
```

### Connection Failed

**Error:** "Cannot connect to MCP server"

**For STDIO:**
```bash
# Check command exists
which figma-mcp

# Test command directly
figma-mcp --version
```

**For HTTP:**
```bash
# Check server is running
curl http://localhost:9222

# Verify port and URL
netstat -an | grep 9222
```

### Tool Not Available

**Issue:** AI can't use a tool from MCP server

**Steps:**
1. Verify server is available: `zk-chat mcp verify`
2. Check tool is defined in server
3. Restart chat session
4. Review server logs

## Security Considerations

### Trust

Only add MCP servers you trust:
- Verify server source
- Review server code
- Check server permissions

### Isolation

MCP servers run in separate processes:
- Can't access zk-chat internals
- Have their own permissions
- Isolated failure domains

### Permissions

Be aware of what servers can access:
- File system access
- Network access
- External API keys

## See Also

- [Available Tools](tools.md) - Built-in tools
- [Plugin Development](../plugins/guide.md) - Create zk-chat plugins
- [Command Line Interface](../usage/cli.md) - MCP commands
- [MCP Documentation](https://modelcontextprotocol.io/) - Official MCP docs
