# Configuration

Learn how to configure Zk-Chat for your specific needs.

## Configuration Storage

Zk-Chat stores its configuration in your Zettelkasten vault:

- **`.zk_chat`** - Configuration file in the vault root
- **`.zk_chat_db/`** - Chroma vector database folder
- **`ZkSystemPrompt.md`** - System prompt file (customizable)

!!! tip "Version Control"
    You may want to add `.zk_chat_db/` to your `.gitignore` file as it can be rebuilt from your documents.

## Vault Configuration

### Setting Vault Path

Specify your vault path when running commands:

```bash
zk-chat interactive --vault /path/to/vault
```

### Bookmarking Vaults

Save frequently used vault paths:

```bash
# Save current vault
zk-chat interactive --vault /path/to/vault --save

# List all bookmarks
zk-chat interactive --list-bookmarks

# Remove a bookmark
zk-chat interactive --remove-bookmark /path/to/vault
```

Once saved, you can run commands without specifying `--vault`:

```bash
zk-chat interactive
```

## Model Configuration

### Selecting a Model

Choose your chat model:

```bash
zk-chat interactive --model qwen2.5:14b
```

Available models depend on your gateway:

=== "Ollama"

    ```bash
    # List available models
    ollama list
    
    # Pull a new model
    ollama pull qwen2.5:14b
    ```

=== "OpenAI"

    Common models:
    - `gpt-4`
    - `gpt-4-turbo`
    - `gpt-3.5-turbo`

### Visual Analysis Model

Enable image analysis with a visual model:

```bash
zk-chat interactive --visual-model llava
```

For OpenAI:

```bash
zk-chat interactive --gateway openai --visual-model gpt-4-vision
```

## Gateway Configuration

### Using Ollama (Default)

Ollama is the default gateway and runs locally:

```bash
# Default - uses Ollama
zk-chat interactive
```

Ensure Ollama is running:

```bash
ollama serve
```

### Using OpenAI

Switch to OpenAI gateway:

```bash
export OPENAI_API_KEY=your_api_key_here
zk-chat interactive --gateway openai --model gpt-4
```

## System Prompt

The system prompt defines how the AI assistant behaves.

### Default System Prompt

On first run, Zk-Chat creates `ZkSystemPrompt.md` in your vault. This file contains instructions for the AI assistant.

### Customizing System Prompt

Edit `ZkSystemPrompt.md` in your vault to customize behavior:

```markdown
# Zk-Chat System Prompt

You are a helpful assistant that...

## Your Capabilities

- Access to the user's Zettelkasten
- Ability to search and read documents
- ...

## Guidelines

- Always cite sources
- Be concise and clear
- ...
```

### Disabling Stored Prompt

To use the default system prompt without creating a file:

```bash
zk-chat interactive --no-store-prompt
```

## MCP Server Configuration

Configure Model Context Protocol servers to extend functionality.

### Add MCP Server

```bash
# Add STDIO server
zk-chat mcp add figma --type stdio --command figma-mcp

# Add HTTP server
zk-chat mcp add chrome --type http --url http://localhost:8080
```

### List MCP Servers

```bash
zk-chat mcp list
```

### Verify Server Availability

```bash
# Verify all servers
zk-chat mcp verify

# Verify specific server
zk-chat mcp verify figma
```

### Remove MCP Server

```bash
zk-chat mcp remove figma
```

## Smart Memory Configuration

### Reset Smart Memory

Clear the smart memory storage:

```bash
zk-chat interactive --reset-memory
```

Smart memory allows the AI to store and retrieve information across sessions.

## Git Integration

### Enable Git Integration

```bash
zk-chat interactive --git
```

This will:

- Initialize a Git repository if one doesn't exist
- Enable Git-related tools (view uncommitted changes, commit with AI-generated messages)

### Unsafe Mode with Git

When allowing AI to modify files, we recommend using Git:

```bash
zk-chat interactive --unsafe --git
```

This provides version control for any changes made by the AI.

## Advanced Options

### Reindex on Startup

Force a reindex when starting a chat session:

```bash
# Incremental reindex
zk-chat interactive --reindex

# Full reindex
zk-chat interactive --reindex --full
```

### Agent Mode

Enable autonomous agent mode for complex tasks:

```bash
zk-chat interactive --agent
```

Agent mode allows the AI to:

- Break down complex tasks
- Use multiple tools in sequence
- Iterate on solutions

### Combining Options

You can combine multiple options:

```bash
zk-chat interactive \
  --vault ~/Documents/Research \
  --model qwen2.5:14b \
  --visual-model llava \
  --agent \
  --git \
  --unsafe \
  --reindex
```

## Configuration Best Practices

1. **Start Simple**: Begin with default settings and customize as needed
2. **Use Bookmarks**: Save frequently used vaults
3. **Version Control**: Use `--git` when enabling `--unsafe` mode
4. **Model Selection**: Choose models that fit your hardware capabilities
5. **Incremental Indexing**: Use regular incremental reindexing, full reindex only when needed
6. **Custom Prompts**: Tailor the system prompt to your specific use case

## Next Steps

- [Interactive Chat](../user-guide/interactive-chat.md) - Learn chat features
- [MCP Servers](../user-guide/mcp-servers.md) - Extend functionality
- [CLI Reference](../reference/cli-commands.md) - Complete command reference
