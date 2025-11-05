# Advanced Settings

Advanced configuration options and customization.

## Configuration File

zk-chat stores configuration in `.zk_chat` in your vault root:

```yaml
vault: /path/to/vault
model: qwen2.5:14b
gateway: ollama
visual_model: llava
```

### Manual Editing

You can edit this file directly:

```bash
# Open in your editor
nano /path/to/vault/.zk_chat
```

Changes take effect on next run.

## Environment Variables

### OpenAI Configuration

```bash
export OPENAI_API_KEY=your_api_key_here
```

### Ollama Configuration

```bash
# Ollama server URL (default: http://localhost:11434)
export OLLAMA_HOST=http://localhost:11434

# Context window size
export OLLAMA_NUM_CTX=8192

# Number of parallel requests
export OLLAMA_NUM_PARALLEL=4
```

## System Prompt Customization

### Location

`ZkSystemPrompt.md` in your vault root.

### Example Customization

```markdown
You are an AI assistant for my personal knowledge base.

## Your Role

- Help me find and connect information
- Suggest improvements to my notes
- Identify gaps in my knowledge

## Style Guidelines

- Be concise but thorough
- Use technical language when appropriate
- Provide examples from my vault
- Always cite sources with wikilinks

## Special Instructions

- When analyzing code, prefer Python examples
- For productivity topics, reference GTD methodology
- Link to related concepts whenever possible

## Constraints

- Don't make assumptions about topics not in my vault
- Ask for clarification when intent is unclear
- Suggest next steps at the end of responses
```

### Disabling System Prompt

Use the default prompt instead:

```bash
zk-chat interactive --no-store-prompt
```

## Embedding Configuration

### Custom Embedding Models

For Ollama, embeddings use the chat model by default. You can use a dedicated embedding model:

```bash
# Pull an embedding model
ollama pull nomic-embed-text

# Use in configuration (manual edit)
embedding_model: nomic-embed-text
```

### Embedding Dimensions

Different models use different dimensions:
- Most models: 384-1536 dimensions
- Changing models requires full reindex

## Index Configuration

### Index Location

Default: `.zk_chat_db/` in vault root.

### Rebuild Frequency

**Incremental (recommended):**
```bash
# After adding/modifying files
zk-chat index rebuild
```

**Full (occasionally):**
```bash
# After major changes
zk-chat index rebuild --full
```

### Automatic Reindexing

```bash
# Rebuild before each session
zk-chat interactive --reindex

# Force full rebuild
zk-chat interactive --reindex --full
```

## Performance Tuning

### For Large Vaults (1000+ docs)

**Use faster models:**
```bash
zk-chat interactive --model phi3:3.8b
```

**Incremental indexing only:**
```bash
# Avoid --full unless necessary
zk-chat index rebuild
```

**Consider SSD storage:**
- Store vault on SSD
- Faster index operations

### For Slow Queries

**Reduce context:**
- Use smaller models
- Limit result count in queries

**Optimize network:**
- Use Ollama (local) instead of OpenAI
- Check network latency

### Memory Management

**For high RAM usage:**
```bash
# Use smaller models
ollama pull qwen2.5:7b

# Limit Ollama memory
export OLLAMA_MAX_LOADED_MODELS=1
```

## Tool Configuration

### Disabling Tools

Tools are enabled by default. To disable specific tools, you would need to customize the zk-chat source code or use MCP servers selectively.

### Custom Tools

Add functionality via:
- [Plugins](../plugins/guide.md) - Python-based extensions
- [MCP Servers](../features/mcp-servers.md) - External tools

## Agent Mode Settings

Agent mode uses the same model but with different behavior:

```bash
# Enable agent mode
zk-chat interactive --agent
```

**Agent characteristics:**
- More autonomous
- Multi-step planning
- Iterative problem solving
- Higher token usage

## Unsafe Mode Configuration

When allowing file modifications:

```bash
# Always use with Git
zk-chat interactive --unsafe --git
```

**Safety tips:**
- Enable Git integration
- Review changes regularly
- Test on copies first
- Keep backups

## Smart Memory Configuration

### Resetting Memory

```bash
# Clear all stored memory
zk-chat interactive --reset-memory
```

### Memory Location

Stored in `.zk_chat_db/` with the index.

### Memory Size

Grows over time. To manage:
```bash
# Periodic reset
zk-chat interactive --reset-memory

# Or full rebuild (resets everything)
zk-chat index rebuild --full
```

## Logging

### Enable Debug Logging

```bash
# Set log level (in environment)
export LOG_LEVEL=DEBUG

# Run zk-chat
zk-chat interactive
```

### Log Location

Logs go to stderr by default. Redirect to file:

```bash
zk-chat interactive 2> zk-chat.log
```

## Multiple Configurations

### Per-Vault Configuration

Each vault has its own `.zk_chat` file:

```bash
# Work vault with GPT-4
cd ~/work-vault
zk-chat interactive --model gpt-4o --gateway openai

# Personal vault with Ollama
cd ~/personal-vault
zk-chat interactive --model qwen2.5:14b
```

### Profile Management

Create wrapper scripts for different profiles:

```bash
#!/bin/bash
# work-chat.sh
export OPENAI_API_KEY=work_key
zk-chat interactive --vault ~/work-vault --model gpt-4o
```

```bash
#!/bin/bash
# personal-chat.sh
zk-chat interactive --vault ~/personal-vault --model qwen2.5:14b
```

## Advanced Use Cases

### Batch Processing

```bash
# Process multiple queries
for query in "${queries[@]}"; do
    zk-chat query "$query" >> results.txt
done
```

### Custom Indexing Schedule

```bash
#!/bin/bash
# cron: 0 */6 * * *
# Rebuild index every 6 hours

cd /path/to/vault
zk-chat index rebuild
```

### Integration with Other Tools

```bash
# Use with git hooks
# .git/hooks/post-commit

#!/bin/bash
zk-chat index rebuild
```

### API Integration

While zk-chat doesn't expose an HTTP API, you can use it in scripts:

```bash
# Get answer programmatically
answer=$(zk-chat query "What is GTD?")
echo "$answer" | mail -s "Query Result" user@example.com
```

## Security Considerations

### API Keys

**Never commit API keys:**
```bash
# Use environment variables
export OPENAI_API_KEY=key

# Or external key management
source ~/.secrets/openai.env
```

### File Permissions

Protect your vault:
```bash
# Vault permissions
chmod 700 /path/to/vault

# Config file permissions
chmod 600 /path/to/vault/.zk_chat
```

### Network Security

**For OpenAI:**
- HTTPS by default
- API keys encrypted in transit

**For Ollama:**
- Local by default
- No external network needed

## Troubleshooting

### Configuration Not Loading

**Check:**
```bash
# Verify file exists
ls -la /path/to/vault/.zk_chat

# Check format
cat /path/to/vault/.zk_chat
```

### Settings Not Persisting

**Solutions:**
- Check file permissions
- Verify vault path
- Look for conflicting arguments

### Performance Issues

**Profile to identify bottleneck:**
```bash
# Time operations
time zk-chat query "test"

# Monitor resources
htop  # during zk-chat use
```

## See Also

- [Model Selection](models.md) - Choosing and configuring models
- [Vault Setup](vault.md) - Vault configuration
- [Index Management](../usage/index-management.md) - Index tuning
- [Command Line Interface](../usage/cli.md) - CLI options
