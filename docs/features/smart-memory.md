# Smart Memory

Smart Memory allows zk-chat to remember important context across chat sessions, providing increasingly personalized responses.

## What is Smart Memory?

Smart Memory is a persistent context storage system that:

- **Stores important facts** from conversations
- **Uses vector embeddings** for semantic similarity search
- **Persists across sessions** - unlike conversation context
- **Provides personalized responses** based on stored preferences

## How It Works

### Automatic Storage

The AI can automatically store information when you ask:

```
You: Remember that I prefer detailed technical explanations

AI: Using tool: store_information
Stored: "User prefers detailed technical explanations"

I'll remember that preference.
```

### Automatic Retrieval

In future sessions, the AI recalls relevant information:

```
[New session]

You: Explain how neural networks work

AI: Using tool: retrieve_information
[Recalls preference for detailed explanations]

[Provides detailed technical explanation]
```

## Use Cases

### User Preferences

```
You: I prefer examples in Python
AI: Stored that preference

[Later...]
You: Show me how to implement a graph
AI: [Provides Python code examples]
```

### Project Context

```
You: I'm working on a distributed systems project
AI: I'll remember that context

[Later...]
You: Help me with my project
AI: [Recalls distributed systems context and provides relevant help]
```

### Important Facts

```
You: Remember that my team uses Git Flow
AI: Stored

[Later...]
You: How should we handle releases?
AI: [Recalls Git Flow usage and provides relevant guidance]
```

## Managing Memory

### Clearing Memory

To reset all stored memory:

```bash
zk-chat interactive --reset-memory
```

!!! warning "Permanent Deletion"
    This permanently deletes all stored memory. Use with caution.

### Memory Storage Location

Smart memory is stored in your vault:

```
your-vault/
├── .zk_chat_db/
│   └── [memory storage]
```

## Best Practices

1. **Be explicit** - Tell the AI what to remember
2. **Review occasionally** - Check if stored context is still relevant
3. **Reset when needed** - Clear memory for fresh starts
4. **Use for preferences** - Store your working style and preferences

## Technical Details

Smart Memory uses:
- **Vector embeddings** - For semantic similarity
- **ChromaDB** - For storage
- **Metadata** - For context and timestamps

## See Also

- [Available Tools](tools.md) - All tool capabilities
- [Interactive Chat](../usage/interactive-chat.md) - Using memory in conversations
