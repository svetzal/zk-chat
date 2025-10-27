# Smart Memory

Smart Memory enables Zk-Chat to remember important information across chat sessions.

## What is Smart Memory?

Smart Memory is a persistent storage system that allows the AI to:

- Store important facts and context
- Retrieve relevant information from past conversations
- Maintain user preferences and patterns
- Build long-term understanding of your knowledge base

## How It Works

### Automatic Storage

During conversations, the AI can choose to store important information:

```
You: I prefer Python over JavaScript for backend development
AI: I'll remember your preference for Python in backend development.
```

The AI decides what to store based on:

- Importance of the information
- Relevance to your knowledge base
- User preferences and patterns

### Automatic Retrieval

When relevant, the AI retrieves stored information:

```
You: Should I use Python or JavaScript for this new API?
AI: Based on your previous preference, I'd recommend Python for backend development.
```

## Storage Location

Smart memory is stored in:

```
your-vault/.zk_chat_db/smart_memory/
```

It uses vector embeddings for semantic search, similar to document indexing.

## Managing Smart Memory

### View Memory Status

Smart memory is integrated into the index status:

```bash
zk-chat index status
```

### Reset Memory

Clear all stored smart memory:

```bash
zk-chat interactive --reset-memory
```

!!! warning "Permanent Action"
    Resetting memory permanently deletes all stored context. This cannot be undone.

### When to Reset

Consider resetting smart memory when:

- Starting fresh with a new project
- AI is using outdated preferences
- Troubleshooting unexpected behavior
- Switching to a different use case

## Use Cases

### Personal Preferences

```
You: I prefer detailed explanations over concise ones
AI: I'll remember to provide detailed explanations.
```

Future conversations will reflect this preference.

### Project Context

```
You: I'm working on a machine learning project about image classification
AI: I'll store this context about your ML image classification project.
```

The AI can reference this in future sessions.

### Custom Definitions

```
You: In my notes, "PKM" means Personal Knowledge Management
AI: I'll remember that PKM stands for Personal Knowledge Management in your notes.
```

The AI will use this definition consistently.

### Recurring Tasks

```
You: When I ask for a summary, include: key points, action items, and next steps
AI: I'll remember to structure summaries with those three sections.
```

## Privacy and Data

### What Gets Stored

- Facts and preferences you share
- Important context from conversations
- Patterns the AI identifies

### What Doesn't Get Stored

- Full conversation transcripts
- Sensitive information (unless explicitly shared)
- Document content (that's in the main index)

### Local Storage

All smart memory data is stored locally in your vault. It:

- Never leaves your machine (with Ollama)
- Is under your control
- Can be deleted at any time

## Best Practices

### Be Explicit

Tell the AI what to remember:

```
You: Please remember that I prefer markdown tables over bullet lists
```

### Regular Review

Occasionally reset if preferences change:

```bash
zk-chat interactive --reset-memory
```

Then re-establish current preferences.

### Combine with System Prompt

For permanent preferences, add to `ZkSystemPrompt.md` instead:

```markdown
## User Preferences
- Always provide detailed explanations
- Format lists as markdown tables
- Include sources for all claims
```

## Troubleshooting

### AI Not Remembering

1. Check that memory wasn't reset
2. Be more explicit about what to remember
3. Verify the information is relevant and important

### AI Using Wrong Information

1. Correct the AI in conversation
2. Reset memory if persistent: `--reset-memory`
3. Add corrections to system prompt

### Performance Issues

If smart memory grows too large:

```bash
# Reset and start fresh
zk-chat interactive --reset-memory
```

## Next Steps

- [Configuration](../getting-started/configuration.md) - Configure system prompt
- [Interactive Chat](interactive-chat.md) - Learn about chat features
- [Index Management](index-management.md) - Manage document index
