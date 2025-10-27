# Configuration Reference

Complete reference for Zk-Chat configuration options.

## Configuration Storage

### Vault-Level Configuration

Stored in `.zk_chat` file in vault root:

```yaml
model: qwen2.5:14b
gateway: ollama
visual_model: llava
last_indexed: 2024-01-15T10:30:00
```

### Global Configuration

MCP servers are stored globally in:

- macOS/Linux: `~/.config/zk-chat/mcp-servers.json`
- Windows: `%APPDATA%\zk-chat\mcp-servers.json`

### System Prompt

Stored in `ZkSystemPrompt.md` in vault root (optional).

## Configuration Options

### Model Selection

**Chat Model:**

```bash
--model, -m MODEL
```

Available models depend on your gateway:

- Ollama: Models you've pulled (check with `ollama list`)
- OpenAI: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`, etc.

**Visual Model:**

```bash
--visual-model MODEL
```

For image analysis capabilities:

- Ollama: `llava`, `bakllava`
- OpenAI: `gpt-4-vision`

### Gateway Selection

```bash
--gateway, -g {ollama|openai}
```

- `ollama`: Use local Ollama instance (default)
- `openai`: Use OpenAI API (requires `OPENAI_API_KEY`)

### Vault Configuration

**Vault Path:**

```bash
--vault, -v PATH
```

Path to your Zettelkasten vault directory.

**Bookmarking:**

```bash
--save                  # Save current vault path
--list-bookmarks        # List saved vault paths
--remove-bookmark PATH  # Remove saved vault path
```

### Safety Options

**Unsafe Mode:**

```bash
--unsafe
```

Allows AI to modify files. **Use with caution!**

**Git Integration:**

```bash
--git
```

Enable Git tools. Recommended with `--unsafe`.

### Agent Configuration

**Agent Mode:**

```bash
--agent
```

Enable autonomous agent for multi-step reasoning.

### Index Options

**Reindex on Start:**

```bash
--reindex              # Incremental reindex
--reindex --full       # Full reindex
```

**Reset Smart Memory:**

```bash
--reset-memory
```

Clear smart memory storage.

### Prompt Storage

**Store System Prompt:**

```bash
--store-prompt         # Store (default)
--no-store-prompt      # Don't store
```

## Default Values

When not specified, Zk-Chat uses these defaults:

```yaml
gateway: ollama
model: (prompted on first run)
visual_model: null
unsafe: false
git: false
agent: false
store_prompt: true
```

## Environment Variables

### OPENAI_API_KEY

Required for OpenAI gateway:

```bash
export OPENAI_API_KEY=sk-...
```

### Optional Variables

These are not currently used but may be in future versions:

```bash
OLLAMA_HOST=http://localhost:11434    # Custom Ollama endpoint
ZK_CHAT_CONFIG_DIR=~/.config/zk-chat # Custom config directory
```

## MCP Server Configuration

MCP servers are configured using the `mcp` commands:

```bash
# Add STDIO server
zk-chat mcp add NAME --type stdio --command COMMAND [--args ARGS]

# Add HTTP server
zk-chat mcp add NAME --type http --url URL
```

Configuration is stored in `mcp-servers.json`:

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
      "url": "http://localhost:8080"
    }
  }
}
```

## System Prompt Configuration

Customize AI behavior by editing `ZkSystemPrompt.md` in your vault:

```markdown
# Zk-Chat System Prompt

You are a helpful assistant with access to the user's Zettelkasten.

## Your Capabilities

- Search and read documents
- Analyze connections between ideas
- Provide context-aware responses

## Guidelines

- Always cite sources from the vault
- Be concise but thorough
- Ask for clarification when needed
```

## Configuration Best Practices

1. **Start Simple**: Use defaults, customize as needed
2. **Document Choices**: Note why you chose specific models/settings
3. **Version Control**: Add `.zk_chat_db/` to `.gitignore`
4. **Backup Configuration**: Keep `.zk_chat` file in version control
5. **Test Settings**: Try different models to find what works best

## Configuration Examples

### Research Setup

```bash
zk-chat interactive \
  --vault ~/research \
  --model qwen2.5:14b \
  --visual-model llava \
  --git \
  --agent
```

### Writing Setup

```bash
zk-chat interactive \
  --vault ~/writing \
  --model phi4:14b \
  --git
```

### Quick Queries

```bash
zk-chat query "question" \
  --vault ~/notes \
  --model qwen2.5:14b
```

## Troubleshooting Configuration

### Configuration Not Saved

Check that:

1. Vault path is writable
2. `.zk_chat` file isn't read-only
3. No permission issues

### Model Not Found

Verify model availability:

```bash
# Ollama
ollama list

# OpenAI
echo $OPENAI_API_KEY
```

### MCP Servers Not Loading

Check:

```bash
zk-chat mcp list
zk-chat mcp verify
```

## Next Steps

- [CLI Commands](cli-commands.md) - Command reference
- [Troubleshooting](troubleshooting.md) - Common issues
- [Getting Started](../getting-started/configuration.md) - Configuration guide
