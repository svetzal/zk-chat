# Quick Start

Get up and running with Zk-Chat in just a few minutes!

## Prerequisites

Before you begin, make sure you have:

- ✅ [Installed Zk-Chat](installation.md)
- ✅ Ollama running (or OpenAI API key configured)
- ✅ A Zettelkasten with markdown files (e.g., an Obsidian vault)

## Your First Chat Session

### Step 1: Start Interactive Chat

```bash
zk-chat interactive --vault /path/to/your/vault
```

Replace `/path/to/your/vault` with the actual path to your Zettelkasten.

### Step 2: Initial Configuration

On first run, Zk-Chat will prompt you to:

1. **Select a chat model**: Choose from available Ollama models (or specify OpenAI model)
2. **Select a visual model** (optional): Choose if you want image analysis capabilities
3. **Index your vault**: Zk-Chat will build an initial index of your documents

!!! info "First-time Indexing"
    The initial indexing may take a few minutes depending on the size of your vault. Subsequent runs will be much faster with incremental updates.

### Step 3: Start Chatting

Once indexing is complete, you'll see the chat prompt:

```
You: 
```

Try asking questions about your knowledge base:

- "What are my thoughts on productivity?"
- "Find documents about machine learning"
- "Summarize my notes on project X"

## Basic Commands

### Ask a Single Question

Don't need an interactive session? Ask a single question:

```bash
zk-chat query "What are my thoughts on productivity?"
```

Or pipe a question from a file:

```bash
cat prompt.txt | zk-chat query
```

### Rebuild Index

If you've added or modified many documents:

```bash
# Quick incremental rebuild
zk-chat index rebuild

# Full rebuild (slower but comprehensive)
zk-chat index rebuild --full
```

### Check Index Status

```bash
zk-chat index status
```

## Common Options

### Specify Vault Path

```bash
zk-chat interactive --vault /path/to/vault
```

### Change Model

```bash
zk-chat interactive --model qwen2.5:14b
```

### Use OpenAI Instead of Ollama

```bash
zk-chat interactive --gateway openai --model gpt-4
```

### Enable Unsafe Mode (Allow File Modifications)

!!! warning "Use with Caution"
    Unsafe mode allows the AI to modify your files. We strongly recommend using `--git` for version control.

```bash
zk-chat interactive --unsafe --git
```

### Use Agent Mode for Complex Tasks

```bash
zk-chat interactive --agent
```

Agent mode allows the AI to perform multi-step reasoning and use tools autonomously.

## Bookmarking Vaults

Save frequently used vault paths:

```bash
# Save current vault as bookmark
zk-chat interactive --vault /path/to/vault --save

# List bookmarks
zk-chat interactive --list-bookmarks

# Remove a bookmark
zk-chat interactive --remove-bookmark /path/to/vault
```

## Example Workflow

Here's a typical workflow:

```bash
# 1. Start chat with your vault
zk-chat interactive --vault ~/Documents/MyVault

# 2. Ask questions
You: What are my key insights about leadership?

# 3. Let AI find and read relevant documents
# The AI will automatically use tools to:
# - Search for relevant documents
# - Read specific documents
# - Extract excerpts
# - Provide a synthesized response

# 4. Follow up with more questions
You: Can you create a summary document of these insights?

# (With --unsafe --git enabled, AI can create the document)
```

## Getting Help

- Use `zk-chat --help` to see all available commands
- Use `zk-chat <command> --help` for command-specific help
- Visit the [User Guide](../user-guide/interactive-chat.md) for detailed features

## Next Steps

- [Configuration Options](configuration.md) - Customize Zk-Chat behavior
- [Interactive Chat Guide](../user-guide/interactive-chat.md) - Learn all chat features
- [Available Tools](../tools/document-management.md) - Discover what Zk-Chat can do
- [Plugin Development](../plugins/overview.md) - Extend Zk-Chat with custom tools
