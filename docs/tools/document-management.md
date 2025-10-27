# Document Management Tools

Zk-Chat provides a comprehensive set of tools for managing and querying your Zettelkasten documents.

## Read-Only Tools

These tools are always available and safe to use:

### Find Documents

Searches for documents based on a semantic query.

**Use cases:**

- Finding relevant documents for a topic
- Discovering related content
- Exploring your knowledge base

**Example:**

```
You: Find documents about machine learning
AI: [Uses Find Documents tool to search and returns matching documents]
```

### Find Excerpts

Retrieves specific passages from documents matching your search criteria.

**Use cases:**

- Finding specific information
- Extracting relevant quotes
- Locating precise context

**Example:**

```
You: Find excerpts about neural networks
AI: [Returns relevant passages from multiple documents]
```

### List Documents

Displays all documents in your Zettelkasten.

**Use cases:**

- Getting an overview of your vault
- Discovering what content you have
- Finding document names

**Example:**

```
You: What documents do I have?
AI: [Lists all documents in your vault]
```

### Read Document

Accesses the full content of a specific document.

**Use cases:**

- Reading complete documents
- Getting full context
- Reviewing document content

**Example:**

```
You: Read the document about project planning
AI: [Reads and displays the full document content]
```

### Resolve WikiLink

Converts wikilinks (e.g., `[[Document Title]]`) to relative file paths.

**Use cases:**

- Following links between documents
- Understanding document relationships
- Navigating your vault structure

**Example:**

```
You: What does [[Project Ideas]] link to?
AI: [Resolves the wikilink to the actual file path]
```

## Write Tools (Unsafe Mode)

These tools require the `--unsafe` flag and allow the AI to modify your vault.

!!! danger "Use with Caution"
    These tools can modify or delete your files. Always use `--git` for version control.

### Write Document

Creates or updates documents in your Zettelkasten.

**Requires:** `--unsafe` flag

**Use cases:**

- Creating new notes
- Updating existing documents
- Generating content based on research

**Example:**

```bash
zk-chat interactive --unsafe --git
```

```
You: Create a summary document of my machine learning notes
AI: [Uses Write Document tool to create a new summary document]
```

### Rename Document

Changes the name of an existing document.

**Requires:** `--unsafe` flag

**Use cases:**

- Organizing your vault
- Standardizing naming conventions
- Fixing typos in file names

**Example:**

```
You: Rename "Old Project Ideas" to "Archive - Project Ideas 2023"
AI: [Renames the document]
```

### Delete Document

Permanently removes a document from your Zettelkasten.

**Requires:** `--unsafe` flag

**Use cases:**

- Removing outdated content
- Cleaning up duplicates
- Vault maintenance

!!! warning "Permanent Action"
    Deleted documents cannot be recovered unless you have backups or version control.

**Example:**

```
You: Delete the draft document about X
AI: [Deletes the specified document]
```

## Using Document Tools

### Implicit Tool Usage

You don't need to explicitly call tools. The AI decides which tools to use:

```
You: What are my thoughts on productivity?
```

The AI will:

1. Use **Find Documents** to search for productivity-related notes
2. Use **Read Document** to access relevant documents
3. Synthesize a response

### Explicit Tool Requests

You can explicitly request tool usage:

```
You: List all my documents
You: Read the document about project X
You: Find documents created this week
```

### Multi-Step Operations

The AI can use multiple tools in sequence:

```
You: Find my most important project notes and create a summary document
```

The AI will:

1. **Find Documents** about projects
2. **Read Document** for each important project
3. **Write Document** to create the summary (with --unsafe)

## Best Practices

### Search Effectively

Be specific in your searches:

- Good: "Find documents about Python web frameworks"
- Less good: "Find Python stuff"

### Review Before Modifying

When using unsafe mode:

1. Ask the AI to show you what it will change
2. Review the changes
3. Confirm or modify the request

### Use Git Integration

Always enable Git when using unsafe mode:

```bash
zk-chat interactive --unsafe --git
```

This provides:

- Version history
- Ability to revert changes
- Change tracking

### Incremental Changes

Make changes incrementally:

1. Start with searches and reads
2. Review the information
3. Then request modifications

## Examples

### Research Workflow

```
You: Find all documents about topic X
AI: [Lists matching documents]

You: Read the document titled "Introduction to X"
AI: [Reads and summarizes the document]

You: What are the key points?
AI: [Extracts and presents key points]

You: Create a summary document of these key points
AI: [With --unsafe, creates a new summary document]
```

### Organization Workflow

```
You: List all documents with "draft" in the title
AI: [Lists draft documents]

You: Rename them to include the date
AI: [With --unsafe, renames documents with dates]

You: Create an index document linking to all drafts
AI: [With --unsafe, creates an index with wikilinks]
```

### Content Discovery

```
You: Find documents I haven't read in a while
AI: [Searches for older documents]

You: What are they about?
AI: [Reads and summarizes each document]

You: Create a "to review" list
AI: [Creates a checklist document]
```

## Next Steps

- [Graph Traversal Tools](graph-traversal.md) - Navigate document relationships
- [Git Integration Tools](git-integration.md) - Version control features
- [Interactive Chat](../user-guide/interactive-chat.md) - Using tools in chat
