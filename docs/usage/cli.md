# Command Line Interface

The zk-chat CLI provides a modern command-based interface for interacting with your Zettelkasten.

## Overview

```bash
zk-chat [OPTIONS] COMMAND [ARGS]...
```

## Available Commands

### `interactive` - Start Interactive Chat

Start an interactive chat session with your Zettelkasten.

```bash
zk-chat interactive [OPTIONS]
```

**Common Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--vault PATH` | `-v` | Path to your Zettelkasten vault |
| `--gateway {ollama,openai}` | `-g` | Model gateway to use |
| `--model MODEL` | `-m` | Specific model to use |
| `--visual-model MODEL` | | Model for visual analysis |
| `--agent` | | Enable autonomous agent mode |
| `--unsafe` | | Allow AI to modify files |
| `--git` | | Enable Git integration |
| `--reindex` | | Rebuild index before starting |
| `--full` | | Force full reindex (use with --reindex) |
| `--reset-memory` | | Clear smart memory |
| `--save` | | Bookmark the vault path |

**Examples:**

```bash
# Basic interactive session
zk-chat interactive --vault ~/Documents/MyVault

# Agent mode with file modification (with Git backup)
zk-chat interactive --agent --unsafe --git

# Use OpenAI instead of Ollama
zk-chat interactive --gateway openai --model gpt-4

# Rebuild index before starting
zk-chat interactive --reindex

# Reset memory and start fresh
zk-chat interactive --reset-memory
```

### `query` - Single Query

Ask a single question without starting an interactive session.

```bash
zk-chat query [OPTIONS] [QUESTION]
```

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--vault PATH` | `-v` | Path to your Zettelkasten vault |
| `--gateway {ollama,openai}` | `-g` | Model gateway to use |
| `--model MODEL` | `-m` | Specific model to use |
| `--agent` | | Enable autonomous agent mode |

**Examples:**

```bash
# Ask a direct question
zk-chat query "What are my thoughts on productivity?"

# Read question from stdin
cat question.txt | zk-chat query

# Use agent mode for complex queries
zk-chat query "Analyze all my productivity notes" --agent
```

### `index` - Manage Search Index

Manage your Zettelkasten's search index.

```bash
zk-chat index COMMAND [OPTIONS]
```

**Subcommands:**

#### `rebuild` - Rebuild Index

```bash
zk-chat index rebuild [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--full` | Force complete rebuild (slower but comprehensive) |

**Examples:**

```bash
# Incremental rebuild (fast, updates only changed files)
zk-chat index rebuild

# Full rebuild (slower, reindexes everything)
zk-chat index rebuild --full
```

#### `status` - Check Index Status

```bash
zk-chat index status
```

Shows information about the current index:
- Number of indexed documents
- Last update time
- Index location

### `mcp` - Manage MCP Servers

Register and manage Model Context Protocol (MCP) servers.

```bash
zk-chat mcp COMMAND [OPTIONS]
```

**Subcommands:**

#### `add` - Add MCP Server

```bash
zk-chat mcp add NAME --type {stdio,http} [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--type {stdio,http}` | Server connection type |
| `--command CMD` | Command to run (for stdio) |
| `--args ARGS` | Command arguments (for stdio) |
| `--url URL` | Server URL (for http) |

**Examples:**

```bash
# Add STDIO server
zk-chat mcp add figma --type stdio --command figma-mcp

# Add STDIO server with arguments
zk-chat mcp add custom --type stdio --command my-server --args "--port 8080"

# Add HTTP server
zk-chat mcp add chrome --type http --url http://localhost:8080
```

#### `list` - List MCP Servers

```bash
zk-chat mcp list
```

Shows all registered MCP servers with their status.

#### `verify` - Verify Server Availability

```bash
zk-chat mcp verify [NAME]
```

Check if MCP servers are available and responding.

**Examples:**

```bash
# Verify all servers
zk-chat mcp verify

# Verify specific server
zk-chat mcp verify figma
```

#### `remove` - Remove MCP Server

```bash
zk-chat mcp remove NAME
```

Remove a registered MCP server.

### `gui` - Launch Graphical Interface

Launch the experimental GUI.

```bash
zk-chat gui launch
```

!!! warning "Experimental Feature"
    The GUI is experimental and uses an older configuration system. It may not have all features available in the CLI.

## Global Options

These options are available for all commands:

| Option | Short | Description |
|--------|-------|-------------|
| `--vault PATH` | `-v` | Path to Zettelkasten vault |
| `--gateway {ollama,openai}` | `-g` | Model gateway (default: ollama) |
| `--model MODEL` | `-m` | Chat model to use |
| `--visual-model MODEL` | | Visual analysis model |
| `--help` | `-h` | Show help message |

## Vault Management

### Bookmarking Vaults

Save frequently used vault paths as bookmarks:

```bash
# Save current vault
zk-chat interactive --vault /path/to/vault --save

# List bookmarks
zk-chat interactive --list-bookmarks

# Remove bookmark
zk-chat interactive --remove-bookmark /path/to/vault
```

Once bookmarked, you can omit the `--vault` parameter for subsequent commands.

## Configuration Storage

zk-chat stores configuration and data in your vault:

- `.zk_chat` - Configuration file
- `.zk_chat_db/` - Vector database
- `ZkSystemPrompt.md` - System prompt (customizable)

## Environment Variables

### OpenAI Configuration

When using the OpenAI gateway:

```bash
export OPENAI_API_KEY=your_api_key_here
```

## Safety Features

### Git Integration

When using `--unsafe` mode (allowing file modifications), we strongly recommend enabling Git:

```bash
zk-chat interactive --unsafe --git
```

This will:
- Initialize a Git repository if one doesn't exist
- Track all changes made by the AI
- Allow you to review and revert changes

### Agent Mode

Agent mode (`--agent`) enables autonomous problem-solving where the AI can:
- Break down complex tasks
- Plan and execute multiple steps
- Use tools iteratively

Use with caution, especially combined with `--unsafe`.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Index error |

## Examples by Use Case

### Research and Discovery

```bash
# Interactive exploration
zk-chat interactive --vault ~/Research

# Quick fact-finding
zk-chat query "List all papers about neural networks"
```

### Content Creation

```bash
# Let AI help create content (with Git safety)
zk-chat interactive --unsafe --git --agent

# Then ask: "Create a summary document of all my machine learning notes"
```

### Maintenance

```bash
# Rebuild index after adding many new files
zk-chat index rebuild --full

# Check index status
zk-chat index status
```

### Integration with External Tools

```bash
# Add MCP servers for extended functionality
zk-chat mcp add browser --type http --url http://localhost:9222

# Verify servers before use
zk-chat mcp verify
```

## Tips and Best Practices

1. **Save frequently used vaults** - Use `--save` to bookmark your main vaults
2. **Rebuild index regularly** - Run `zk-chat index rebuild` after adding new content
3. **Use Git with --unsafe** - Always enable Git when allowing file modifications
4. **Start simple** - Try basic queries before using agent mode
5. **Check help frequently** - Use `--help` on any command for details

## See Also

- [Interactive Chat Guide](interactive-chat.md) - Deep dive into chat features
- [Index Management](index-management.md) - Detailed index management
- [MCP Servers](../features/mcp-servers.md) - MCP server integration guide
