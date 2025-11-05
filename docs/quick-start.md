# Quick Start

This tutorial will guide you through your first zk-chat session.

## Prerequisites

Before starting, ensure you have:

- ✅ Installed zk-chat (see [Installation Guide](installation.md))
- ✅ Ollama installed and running (or OpenAI API key set)
- ✅ A Zettelkasten with some markdown files

## Your First Chat Session

### Step 1: Start Interactive Mode

Open your terminal and run:

```bash
zk-chat interactive --vault /path/to/your/vault
```

Replace `/path/to/your/vault` with the actual path to your Zettelkasten folder.

!!! tip "Save Your Vault Path"
    Add the `--save` flag to bookmark this vault path:
    ```bash
    zk-chat interactive --vault /path/to/your/vault --save
    ```
    Next time, you can just run `zk-chat interactive` without specifying the path.

### Step 2: Model Selection

On first run, you'll be prompted to select a model:

```
Available models:
1. qwen2.5:14b
2. phi4:14b
3. llama3.3
...

Select a model (1-N):
```

Choose a model by entering its number. The tool will use this model for all chat interactions.

### Step 3: Visual Analysis (Optional)

Next, you'll be asked about visual analysis:

```
Do you want to enable visual analysis? (y/n):
```

- Type `y` if you want the AI to analyze images in your vault
- Type `n` to skip this feature (you can enable it later)

If you choose yes, select a vision-capable model (e.g., `llava`, `bakllava`).

### Step 4: Index Building

zk-chat will now index your documents:

```
Building index...
Indexed 150 documents
Ready to chat!
```

This creates a searchable vector database of your content.

### Step 5: Start Chatting!

The chat prompt will appear:

```
You:
```

Try asking some questions:

**Example 1: Find Related Documents**
```
You: What documents do I have about productivity?
```

The AI will search your vault and list relevant documents.

**Example 2: Get Insights**
```
You: Summarize my thoughts on time management
```

The AI will find and analyze relevant documents, then provide a summary.

**Example 3: Navigate Connections**
```
You: What concepts are connected to "Getting Things Done"?
```

The AI will explore wikilinks and related documents.

## Understanding Tool Usage

As the AI responds, you may see it using tools:

```
Using tool: find_documents
Query: productivity

Found 5 documents:
- Daily Practices.md
- Deep Work Notes.md
- GTD System.md
...
```

This shows the AI actively searching your vault to answer your question.

## Common First Queries

Here are some useful queries to try:

### Discovery
```
- "List all my documents about [topic]"
- "What are the main themes in my vault?"
- "Show me my most connected notes"
```

### Analysis
```
- "Summarize my notes on [topic]"
- "What are the key ideas in [document name]?"
- "How do [concept A] and [concept B] relate in my notes?"
```

### Navigation
```
- "What documents link to [document name]?"
- "Find connection paths between [doc A] and [doc B]"
- "What are my hub documents?" (most linked-to documents)
```

## Exiting the Chat

To exit the chat session, type:

```
exit
```

or press `Ctrl+D`.

## Next Steps

### Enable Advanced Features

For more powerful capabilities, try:

**Agent Mode** - Let the AI work autonomously on complex tasks:
```bash
zk-chat interactive --agent
```

**Unsafe Mode with Git** - Allow the AI to create/modify documents with version control:
```bash
zk-chat interactive --unsafe --git
```

!!! warning "Unsafe Mode"
    Only use `--unsafe` if you want the AI to modify your vault. We strongly recommend using `--git` for version control when enabling this option.

### Explore Single Queries

For quick questions without a chat session:

```bash
zk-chat query "What are my thoughts on meditation?"
```

### Manage Your Index

If you add new documents to your vault:

```bash
# Incremental rebuild (fast)
zk-chat index rebuild

# Full rebuild (comprehensive)
zk-chat index rebuild --full
```

### Try Plugins

Extend functionality with plugins:

```bash
# Install Wikipedia plugin
pipx inject zk-chat zk-rag-wikipedia

# Now you can ask the AI to look up information on Wikipedia
```

## Tips for Effective Use

1. **Be Specific**: The more specific your query, the better the results
   - ❌ "Tell me about notes"
   - ✅ "What are the key concepts in my productivity notes?"

2. **Use Natural Language**: Ask questions as you would to a person
   - ✅ "How do I implement the GTD system?"
   - ✅ "Find documents related to deep work"

3. **Leverage Context**: The AI remembers your conversation
   - "Tell me more about that"
   - "Can you elaborate on the second point?"

4. **Explore Connections**: Ask about relationships between ideas
   - "How does [concept A] relate to [concept B]?"
   - "What's the connection between these documents?"

## Troubleshooting

### Index Not Found

If you see "Index not found", rebuild it:

```bash
zk-chat index rebuild
```

### Model Not Available

If the selected model isn't available:

1. Check Ollama has the model:
   ```bash
   ollama list
   ```

2. Pull the model if needed:
   ```bash
   ollama pull qwen2.5:14b
   ```

### Slow Responses

If responses are slow:

- Use a smaller model (fewer parameters)
- Close other applications to free up RAM
- Consider using OpenAI's API instead of local models

## Learn More

- [Command Line Interface](usage/cli.md) - Complete CLI reference
- [Available Tools](features/tools.md) - What the AI can do
- [Smart Memory](features/smart-memory.md) - How context is preserved
- [Plugin Development](plugins/guide.md) - Create custom tools
