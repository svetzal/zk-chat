# CLI Commands Reference

Complete reference for all Zk-Chat command-line commands.

## Global Options

Available for all commands:

```
--vault, -v PATH        Path to Zettelkasten vault
--gateway, -g           LLM gateway (ollama|openai)
--model, -m MODEL       Chat model name
--visual-model MODEL    Visual analysis model name
--help                  Show help message
```

## Commands

### interactive

Start an interactive chat session.

```bash
zk-chat interactive [OPTIONS]
```

**Options:**

```
--agent                 Use autonomous agent mode
--unsafe                Allow AI to modify files
--git                   Enable Git integration
--store-prompt          Store system prompt in vault (default)
--no-store-prompt       Don't store system prompt
--reindex               Rebuild index before starting
--full                  Full reindex (use with --reindex)
--reset-memory          Clear smart memory storage
--save                  Save vault path as bookmark
--remove-bookmark PATH  Remove bookmarked vault path
--list-bookmarks        List all bookmarked vault paths
```

**Examples:**

```bash
# Basic interactive chat
zk-chat interactive --vault /path/to/vault

# With agent mode and Git
zk-chat interactive --agent --git

# Allow file modifications (with Git for safety)
zk-chat interactive --unsafe --git

# Full reindex before starting
zk-chat interactive --reindex --full

# Reset smart memory
zk-chat interactive --reset-memory
```

### query

Ask a single question without interactive session.

```bash
zk-chat query [QUERY] [OPTIONS]
```

**Options:**

Same global options as `interactive`, plus:

```
--agent                 Use autonomous agent mode
```

**Examples:**

```bash
# Direct question
zk-chat query "What are my thoughts on productivity?"

# From file
cat prompt.txt | zk-chat query

# With agent mode
zk-chat query "Analyze my project notes" --agent

# Specify model
zk-chat query "Your question" --model qwen2.5:14b
```

### index

Manage the document index.

#### index status

Check index status.

```bash
zk-chat index status [OPTIONS]
```

**Example:**

```bash
zk-chat index status --vault /path/to/vault
```

#### index rebuild

Rebuild the document index.

```bash
zk-chat index rebuild [OPTIONS]
```

**Options:**

```
--full                  Full rebuild (slower, comprehensive)
```

**Examples:**

```bash
# Incremental rebuild (fast)
zk-chat index rebuild --vault /path/to/vault

# Full rebuild
zk-chat index rebuild --full --vault /path/to/vault
```

### mcp

Manage Model Context Protocol servers.

#### mcp add

Add a new MCP server.

```bash
zk-chat mcp add NAME --type TYPE [OPTIONS]
```

**Options:**

```
--type TYPE            Server type (stdio|http)
--command CMD          Command for STDIO servers
--url URL              URL for HTTP servers
--args ARGS            Additional arguments (optional)
```

**Examples:**

```bash
# Add STDIO server
zk-chat mcp add figma --type stdio --command figma-mcp

# Add HTTP server
zk-chat mcp add chrome --type http --url http://localhost:8080

# Add STDIO server with args
zk-chat mcp add custom --type stdio --command custom-mcp --args "--verbose"
```

#### mcp list

List all registered MCP servers.

```bash
zk-chat mcp list
```

#### mcp verify

Verify MCP server availability.

```bash
zk-chat mcp verify [NAME]
```

**Examples:**

```bash
# Verify all servers
zk-chat mcp verify

# Verify specific server
zk-chat mcp verify figma
```

#### mcp remove

Remove a registered MCP server.

```bash
zk-chat mcp remove NAME
```

**Example:**

```bash
zk-chat mcp remove figma
```

### gui

GUI-related commands (experimental).

#### gui launch

Launch the graphical interface.

```bash
zk-chat gui launch
```

**Note:** The GUI uses a different configuration system and is experimental.

## Environment Variables

### OPENAI_API_KEY

Required when using OpenAI gateway.

```bash
export OPENAI_API_KEY=your_api_key_here
zk-chat interactive --gateway openai --model gpt-4
```

## Configuration Files

### .zk_chat

Configuration file stored in vault root. Created automatically on first run.

Contains:

- Selected model
- Gateway type
- Visual model (if configured)
- Other preferences

### ZkSystemPrompt.md

System prompt file in vault root. Defines AI assistant behavior.

To disable creation:

```bash
zk-chat interactive --no-store-prompt
```

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Configuration error
- `130`: Interrupted (Ctrl+C)

## Tips

### Multiple Vaults

Work with different vaults using bookmarks:

```bash
# Bookmark work vault
zk-chat interactive --vault ~/work-vault --save

# Bookmark personal vault
zk-chat interactive --vault ~/personal-vault --save

# List bookmarks
zk-chat interactive --list-bookmarks

# Use without specifying path
cd ~/work-vault && zk-chat interactive
```

### Script Integration

Use in scripts:

```bash
#!/bin/bash
result=$(zk-chat query "Your question" --vault /path/to/vault)
echo "$result" > output.txt
```

### Chaining Commands

```bash
# Rebuild index then chat
zk-chat index rebuild --full && zk-chat interactive
```

## Next Steps

- [Configuration Options](configuration.md) - Detailed configuration guide
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [User Guide](../user-guide/interactive-chat.md) - Feature guides
