# Available Tools

zk-chat provides a comprehensive set of tools that extend the AI's capabilities when working with your Zettelkasten.

## Document Management Tools

### Find Documents

**Purpose:** Locate relevant documents based on semantic search.

**When to use:**
- "What documents do I have about [topic]?"
- "Find notes related to [concept]"
- "Show me documents about [keyword]"

**Example:**
```
You: What documents do I have about productivity?

AI: Using tool: find_documents
Found 8 documents:
- GTD System.md
- Deep Work Notes.md
- Time Management.md
...
```

### Find Excerpts

**Purpose:** Retrieve specific passages from documents.

**When to use:**
- "Find passages about [specific topic]"
- "Show me excerpts mentioning [keyword]"
- "What do my notes say about [concept]"

**Example:**
```
You: What do my notes say about Pomodoro technique?

AI: Using tool: find_excerpts
Found 3 relevant passages:
1. In "Time Management.md":
   "The Pomodoro technique involves 25-minute focused work sessions..."
```

### List Documents

**Purpose:** Display all documents in your Zettelkasten.

**When to use:**
- "List all my documents"
- "Show me everything in my vault"
- "What files do I have?"

### Read Document

**Purpose:** Access the full content of a specific document.

**When to use:**
- "Read [document name]"
- "Show me the contents of [file]"
- "What's in [document]?"

**Example:**
```
You: Read my GTD System notes

AI: Using tool: read_document
Path: GTD System.md

[Full document content displayed]
```

### Write Document

**Purpose:** Create or update documents.

**Requirements:** `--unsafe` flag

**When to use:**
- "Create a document about [topic]"
- "Update [document] with [information]"
- "Write my notes to [filename]"

!!! warning "Requires --unsafe Flag"
    File modification tools only work with the `--unsafe` flag enabled.

### Rename Document

**Purpose:** Change document names.

**Requirements:** `--unsafe` flag

**When to use:**
- "Rename [old name] to [new name]"
- "Change the name of [document]"

### Delete Document

**Purpose:** Remove documents from your Zettelkasten.

**Requirements:** `--unsafe` flag

**When to use:**
- "Delete [document]"
- "Remove [file]"

!!! danger "Permanent Deletion"
    Use with extreme caution. Consider using `--git` for safety.

## Visual Analysis Tools

### Analyze Image

**Purpose:** Examine and describe images in your vault.

**Requirements:** Visual model configured

**When to use:**
- "What's in the image at [path]?"
- "Describe [image file]"
- "Analyze the chart in [image]"

**Example:**
```
You: What's in the diagram at assets/architecture.png?

AI: Using tool: analyze_image
Path: assets/architecture.png

The image shows a system architecture diagram with three main components:
1. Frontend layer (React application)
2. API layer (REST endpoints)
3. Database layer (PostgreSQL)
...
```

**Supported formats:**
- PNG
- JPEG
- GIF
- Other common image formats

## Navigation Tools

### Resolve WikiLink

**Purpose:** Convert wikilinks to file paths.

**When to use:**
- Internal navigation between documents
- Following wikilink references
- Understanding document connections

**Example:**
```
[[Getting Things Done]] → notes/Getting Things Done.md
```

## Graph Traversal Tools

### Extract Wikilinks

**Purpose:** Fast extraction of all wikilinks from documents.

**When to use:**
- "What documents does [file] link to?"
- "Show me all links in [document]"
- "Extract wikilinks from [file]"

**Output includes:**
- Link text
- Line numbers
- Surrounding context

### Find Backlinks

**Purpose:** Discover what documents link TO a target document.

**When to use:**
- "What links to [document]?"
- "Show me backlinks for [file]"
- "What documents reference [topic]?"

**Example:**
```
You: What documents link to "Getting Things Done"?

AI: Using tool: find_backlinks
Target: Getting Things Done.md

Found 5 documents with backlinks:
1. Daily Workflow.md (2 links)
2. Productivity System.md (1 link)
3. Project Management.md (3 links)
...
```

### Find Forward Links

**Purpose:** Discover what documents a source document links TO.

**When to use:**
- "What does [document] link to?"
- "Show me forward links from [file]"
- "What documents are referenced by [file]?"

### Link Path Finding

**Purpose:** Find connection paths between documents through wikilinks.

**When to use:**
- "How are [doc A] and [doc B] connected?"
- "Find paths between [concept A] and [concept B]"
- "Show connections from [source] to [target]"

**Example:**
```
You: How are "Deep Work" and "Flow State" connected?

AI: Using tool: link_path_finding
Source: Deep Work.md
Target: Flow State.md

Found 2 connection paths:
1. Deep Work → Focus Techniques → Flow State
2. Deep Work → Productivity → Flow State
```

### Link Metrics

**Purpose:** Analyze connectivity patterns and identify hub documents.

**When to use:**
- "What are my most connected documents?"
- "Show me hub documents"
- "Analyze my vault's structure"

**Metrics provided:**
- Incoming links (backlink count)
- Outgoing links (forward link count)
- Total connectivity score
- Hub identification

## Smart Memory Tools

### Store Information

**Purpose:** Save important facts and context for future sessions.

**When to use:**
- "Remember that I prefer [preference]"
- "Store this information: [fact]"
- "Save this context for later"

**Example:**
```
You: Remember that I'm a software developer focusing on distributed systems

AI: Using tool: store_information
Stored: "User is a software developer focusing on distributed systems"

I'll remember that for future conversations.
```

### Retrieve Information

**Purpose:** Recall previously stored information.

**When to use:**
- Automatic - the AI uses this when relevant
- Provides context from previous sessions
- Enables personalized responses

## Git Integration Tools

### View Uncommitted Changes

**Purpose:** Show pending changes in your vault.

**Requirements:** `--git` flag

**When to use:**
- "What files have changed?"
- "Show uncommitted changes"
- "What did I modify?"

### Commit Changes

**Purpose:** Commit changes with AI-generated commit messages.

**Requirements:** `--git` and `--unsafe` flags

**When to use:**
- "Commit these changes"
- "Save my work"
- "Create a commit"

## Tool Plugins

Additional tools can be added via plugins:

### Wikipedia Lookup

**Plugin:** `zk-rag-wikipedia`

**Installation:**
```bash
pipx inject zk-chat zk-rag-wikipedia
```

**Purpose:** Look up information on Wikipedia and create documents.

**Example:**
```
You: Look up Alan Turing on Wikipedia

AI: Using tool: lookup_topic_on_wikipedia
Topic: Alan Turing

[Wikipedia summary]

You: Create a document from that

AI: Using tool: write_document
Created: @Alan Turing.md
```

### Image Generator

**Plugin:** `zk-rag-image-generator`

**Installation:**
```bash
pipx inject zk-chat zk-rag-image-generator
```

**Purpose:** Generate images using Stable Diffusion.

**Example:**
```
You: Generate an image of a serene mountain landscape

AI: Using tool: generate_image
Generated: serene-mountain-landscape.png

The image has been saved. You can embed it with:
![image](serene-mountain-landscape.png)
```

## How Tools Work

### Tool Selection

The AI automatically selects appropriate tools based on your request:

1. **Understands your intent** - What are you trying to do?
2. **Identifies relevant tools** - Which tools can help?
3. **Executes tools** - Calls tools with appropriate parameters
4. **Synthesizes results** - Combines tool outputs into a response

### Tool Transparency

You see exactly what tools are being used:

```
You: Find documents about machine learning and summarize them

AI: Using tool: find_documents
Query: machine learning
[Results...]

Using tool: read_document
Path: Neural Networks.md
[Content...]

Using tool: read_document
Path: Deep Learning.md
[Content...]

[AI synthesizes a summary from the read documents]
```

### Tool Chaining

Tools can be used in sequence:

```
1. find_documents - Find relevant files
2. read_document - Read each file
3. store_information - Remember key points
4. write_document - Create summary (if --unsafe)
```

## Best Practices

### Effective Tool Usage

1. **Be specific** - Clear requests help the AI choose the right tools
2. **Trust the process** - The AI knows which tools to use
3. **Review results** - Check tool outputs for accuracy
4. **Use agent mode** - For complex multi-tool tasks

### Safety

1. **Start read-only** - Use tools without `--unsafe` first
2. **Enable Git** - Use `--git` when allowing modifications
3. **Review changes** - Check what was created/modified
4. **Use incrementally** - Test with small changes first

## Creating Custom Tools

You can extend zk-chat with custom tools via plugins.

See [Plugin Development Guide](../plugins/guide.md) for details.

## See Also

- [Smart Memory](smart-memory.md) - Deep dive into memory system
- [Graph Traversal](graph-traversal.md) - Link analysis details
- [Visual Analysis](visual-analysis.md) - Image analysis guide
- [Git Integration](git-integration.md) - Version control features
- [Plugin Guide](../plugins/guide.md) - Create custom tools
