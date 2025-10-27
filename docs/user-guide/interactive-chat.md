# Interactive Chat

The interactive chat mode is the primary way to interact with your Zettelkasten through Zk-Chat.

## Starting Interactive Chat

```bash
zk-chat interactive --vault /path/to/vault
```

Or, if you've saved a bookmark:

```bash
zk-chat interactive
```

## Chat Interface

Once started, you'll see the chat prompt:

```
You: 
```

Type your message and press Enter. The AI will respond based on:

- Your question
- Context from your Zettelkasten
- Previous conversation history

## Basic Interactions

### Asking Questions

Simply ask questions about your knowledge base:

```
You: What are my notes about machine learning?
```

The AI will:

1. Search your documents for relevant content
2. Read relevant documents
3. Synthesize a response based on your notes

### Follow-up Questions

The AI maintains conversation context:

```
You: What are my notes about machine learning?
AI: [Provides summary from your notes]

You: Can you elaborate on the neural networks part?
AI: [Provides detailed information about neural networks from your notes]
```

### Requesting Actions

With appropriate flags, you can request actions:

```
You: Create a summary document of my machine learning notes
```

!!! warning "Unsafe Mode Required"
    File creation and modification require `--unsafe` flag.

## Chat Modes

### Standard Mode (Default)

Standard mode provides direct Q&A with tool usage:

```bash
zk-chat interactive
```

- Single-turn tool usage
- Direct responses
- Fast and predictable

### Agent Mode

Agent mode enables autonomous multi-step reasoning:

```bash
zk-chat interactive --agent
```

- Multi-step problem solving
- Iterative tool usage
- Complex task automation
- Self-reflection and correction

Example agent mode tasks:

- "Find all documents about project X, analyze common themes, and create a summary"
- "Research topic Y in my notes and create a mind map"
- "Identify gaps in my knowledge about Z"

## Available Commands

### Exit the Chat

```
You: exit
```

Or press `Ctrl+C`.

### Clear Screen

The chat history remains in memory even if you clear the terminal screen.

## Tool Usage

The AI has access to various tools:

### Document Management

- **Find Documents**: Searches for documents by query
- **Find Excerpts**: Retrieves specific passages
- **List Documents**: Shows all documents
- **Read Document**: Reads full document content

With `--unsafe` flag:

- **Write Document**: Creates or updates documents
- **Rename Document**: Renames documents
- **Delete Document**: Removes documents

### Graph Traversal

- **Extract Wikilinks**: Finds all wikilinks in documents
- **Find Backlinks**: Discovers what links TO a document
- **Find Forward Links**: Discovers what a document links TO
- **Link Path Finding**: Finds connection paths between documents
- **Link Metrics**: Analyzes connectivity patterns

### Smart Memory

- **Store Information**: Saves important facts for later
- **Retrieve Information**: Recalls stored information

### Visual Analysis

With `--visual-model` configured:

- **Analyze Image**: Examines and describes images

### Git Integration

With `--git` flag:

- **View Uncommitted Changes**: Shows pending changes
- **Commit Changes**: Commits with AI-generated messages

## Chat Best Practices

### Be Specific

Instead of:

```
You: Tell me about productivity
```

Try:

```
You: What are the key productivity techniques I've documented?
```

### Break Down Complex Tasks

For complex requests, consider:

1. Using agent mode (`--agent`)
2. Breaking into multiple questions
3. Reviewing intermediate results

### Leverage Context

The AI maintains conversation history:

```
You: Find documents about Python
AI: [Lists Python documents]

You: Read the first one
AI: [Reads and summarizes]

You: What libraries does it mention?
AI: [Extracts library information]
```

### Cite Sources

Ask the AI to cite sources:

```
You: What are my thoughts on testing? Please cite specific documents.
```

## Advanced Features

### Multi-turn Conversations

The AI remembers the conversation:

```
You: What are my thoughts on leadership?
AI: [Provides summary]

You: Can you organize those into categories?
AI: [Organizes into categories using previous response]

You: Create a document with this organization
AI: [With --unsafe, creates the document]
```

### Context Management

Smart Memory automatically stores important information:

- Facts mentioned in conversation
- User preferences
- Important connections

This information persists across sessions.

### Visual Analysis Workflow

With visual model configured:

```
You: What's in the image at diagrams/architecture.png?
AI: [Analyzes and describes the image]

You: Based on that diagram, what are the main components?
AI: [Extracts components from visual analysis]
```

## Keyboard Shortcuts

- **Ctrl+C**: Exit chat
- **Ctrl+D**: Exit chat (alternative)
- **Up/Down**: Navigate command history (terminal dependent)

## Troubleshooting

### Chat Not Responding

1. Check that Ollama is running (or OpenAI API key is set)
2. Verify the model is available: `ollama list`
3. Check index status: `zk-chat index status`

### Slow Responses

- Larger models are slower but more capable
- Consider using a smaller model for faster responses
- Agent mode is slower due to multi-step reasoning

### Tool Not Working

- Some tools require specific flags (`--unsafe`, `--git`)
- Verify vault path is correct
- Check that documents are in markdown format

### Out of Context

If conversation becomes confused:

1. Exit and restart chat (clears conversation context)
2. Be more specific in your questions
3. Use `--reset-memory` to clear smart memory

## Next Steps

- [Single Queries](single-queries.md) - One-off questions without interactive session
- [Index Management](index-management.md) - Keep your index up to date
- [Available Tools](../tools/document-management.md) - Learn about all available tools
- [Agent Mode Details](../reference/cli-commands.md#interactive) - Advanced autonomous capabilities
