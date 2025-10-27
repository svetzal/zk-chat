# Interactive Chat

The interactive chat mode is the primary way to interact with your Zettelkasten through zk-chat.

## Starting a Session

```bash
zk-chat interactive --vault /path/to/vault
```

## Chat Interface

Once started, you'll see a simple prompt:

```
You:
```

Type your message and press Enter. The AI will process your request and respond.

## Conversation Flow

The AI maintains context throughout your conversation:

```
You: What documents do I have about machine learning?

AI: I found 12 documents related to machine learning:
- Neural Networks Basics.md
- Deep Learning Overview.md
- CNN Architecture.md
...

You: Tell me more about the CNN document

AI: [Reads and summarizes CNN Architecture.md]

You: How does that relate to my other notes?

AI: [Searches for connections and explains relationships]
```

## Understanding Tool Usage

As the AI works, it will show you which tools it's using:

```
Using tool: find_documents
Query: machine learning

Found 12 documents...

Using tool: read_document
Path: CNN Architecture.md

[Document content]
```

This transparency helps you understand how the AI is searching your vault.

## Chat Modes

### Standard Mode (Default)

In standard mode, the AI responds to each query individually using available tools.

**Best for:**
- Quick questions
- Document searches
- Simple analysis tasks

**Example:**
```bash
zk-chat interactive
```

### Agent Mode

Agent mode enables autonomous problem-solving for complex tasks.

**Best for:**
- Multi-step research tasks
- Comprehensive analysis
- Creating new documents
- Complex queries requiring planning

**Example:**
```bash
zk-chat interactive --agent
```

In agent mode, the AI can:
- Break down complex requests into steps
- Plan and execute multi-step workflows
- Iterate on results until complete
- Use multiple tools in sequence

**Example conversation:**
```
You: Create a comprehensive summary of all my productivity notes

AI: I'll help you create that summary. Let me:
1. Find all productivity-related documents
2. Read and analyze each one
3. Identify key themes
4. Create a structured summary document

[Proceeds to execute each step autonomously]
```

## File Modification Mode

By default, zk-chat is **read-only**. To allow the AI to create or modify files, use the `--unsafe` flag:

```bash
zk-chat interactive --unsafe
```

!!! warning "Use with Caution"
    The `--unsafe` flag allows the AI to:
    - Create new documents
    - Modify existing documents
    - Rename documents
    - Delete documents
    
    Always use with `--git` for safety!

### Safe File Modifications with Git

The recommended way to enable file modifications is with Git integration:

```bash
zk-chat interactive --unsafe --git
```

This will:
- Initialize a Git repository in your vault (if needed)
- Track all changes made by the AI
- Allow you to review and revert changes

**Example workflow:**
```
You: Create a new document summarizing my machine learning notes

AI: [Creates document using write_document tool]

Created: ML Summary.md

You: [Later, if you want to undo]
$ git log          # See what was changed
$ git revert HEAD  # Undo the last change
```

## Advanced Features

### Smart Memory

The AI can remember important information across sessions:

```
You: Remember that I prefer detailed technical explanations

AI: I'll remember that preference.
[Stores in smart memory]

[In a later session...]

You: Explain neural networks

AI: [Provides detailed technical explanation based on stored preference]
```

To clear smart memory:
```bash
zk-chat interactive --reset-memory
```

### Visual Analysis

If you've configured a visual model, you can ask about images:

```
You: What's in the image at diagrams/architecture.png?

AI: [Analyzes image using visual model]
The image shows a system architecture diagram with...
```

### Wikilink Navigation

The AI understands wikilinks in your documents:

```
You: What documents link to "Getting Things Done"?

AI: [Uses find_backlinks tool]
5 documents link to "Getting Things Done":
- Daily Workflow.md
- Productivity System.md
...

You: Show me the forward links from that document

AI: [Uses find_forward_links tool]
"Getting Things Done" links to:
- Next Actions.md
- Context Lists.md
...
```

### Connection Discovery

Find how different ideas connect:

```
You: How are "Deep Work" and "Flow State" connected in my vault?

AI: [Uses link_path_finding tool]
Found 2 connection paths:
1. Deep Work → Focus Techniques → Flow State
2. Deep Work → Productivity → Flow State
```

## Conversation Management

### Continuing Context

The AI remembers your conversation within a session:

```
You: List my productivity documents

AI: [Lists documents]

You: Read the first one

AI: [Reads the first document from the previous list]
```

### Starting Fresh

Each new session starts with a clean context, but smart memory persists:

```bash
# Session 1
zk-chat interactive
You: Remember I'm a software developer
AI: Stored in memory

# Session 2 (later)
zk-chat interactive
You: Help me with my notes
AI: [Recalls you're a software developer from memory]
```

## Keyboard Shortcuts

- **Ctrl+D** - Exit the chat session
- **Ctrl+C** - Cancel current input
- Type `exit` or `quit` - Exit gracefully

## Example Conversations

### Research and Discovery

```
You: What are the main themes in my vault?

AI: [Analyzes document titles and content]
The main themes appear to be:
1. Software Development (45 documents)
2. Productivity (32 documents)
3. Machine Learning (28 documents)
...

You: Show me how software development and machine learning overlap

AI: [Finds connections]
12 documents discuss both topics, including:
- ML in Production Systems.md
- Software Design for ML.md
...
```

### Content Creation

```
You: Create a weekly review template in my templates folder

AI: I'll need the --unsafe flag to create files. 
Please restart with: zk-chat interactive --unsafe --git

[After restarting with --unsafe --git]

You: Create a weekly review template

AI: [Creates file]
Created: templates/Weekly Review.md

The template includes sections for:
- Accomplishments
- Challenges
- Next week's priorities
...
```

### Analysis

```
You: Summarize my thoughts on remote work

AI: [Finds and reads relevant documents]
Based on 8 documents about remote work, your main thoughts are:

1. Communication is critical...
2. Async work enables deep focus...
3. Tools and processes need adaptation...

Key documents:
- Remote Work Best Practices.md
- Team Communication.md
...
```

## Tips for Effective Conversations

### Be Specific

❌ "Tell me about my notes"
✅ "Summarize my notes about GTD methodology"

### Use Natural Language

✅ "How do I implement the Zettelkasten method?"
✅ "Find all documents mentioning 'atomic notes'"
✅ "What's the connection between these two concepts?"

### Leverage Context

The AI remembers your conversation:
```
You: Show me documents about productivity
AI: [Shows list]

You: Read the third one
AI: [Knows which list you're referring to]
```

### Ask for Clarification

```
You: Explain that in simpler terms
You: Can you give me more details about the second point?
You: What do you mean by that?
```

### Request Different Formats

```
You: Explain this as a bullet list
You: Can you format that as a table?
You: Give me a step-by-step guide
```

## Troubleshooting

### AI Not Finding Documents

**Problem:** The AI says it can't find documents you know exist.

**Solutions:**
```bash
# Rebuild the index
zk-chat index rebuild

# Or force a full rebuild
zk-chat index rebuild --full
```

### Responses Too Generic

**Problem:** The AI isn't using your documents, just general knowledge.

**Solutions:**
- Be more specific about wanting information from your vault
- Ask explicitly: "According to my notes, what..."
- Use agent mode for more thorough searching

### Memory Not Working

**Problem:** The AI doesn't remember previous preferences.

**Check:**
```bash
# Make sure you haven't reset memory
# The reset flag clears all stored memory:
# zk-chat interactive --reset-memory
```

**Note:** Regular conversation context only persists within a single session. Only smart memory persists across sessions.

### Tools Not Working

**Problem:** The AI isn't using tools or tools fail.

**Check:**
1. Vault path is correct
2. Documents exist and are readable
3. Index is up to date

```bash
# Verify vault
ls /path/to/vault

# Rebuild index
zk-chat index rebuild
```

## See Also

- [Command Line Interface](cli.md) - Full CLI reference
- [Available Tools](../features/tools.md) - What the AI can do
- [Smart Memory](../features/smart-memory.md) - How memory works
- [Git Integration](../features/git-integration.md) - Using Git for safety
