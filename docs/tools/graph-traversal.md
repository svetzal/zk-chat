# Graph Traversal Tools

Graph traversal tools help you navigate and analyze the link structure of your Zettelkasten.

## Understanding Your Knowledge Graph

Your Zettelkasten is a knowledge graph where:

- **Nodes** = Documents
- **Edges** = WikiLinks (e.g., `[[Document Title]]`)

Graph traversal tools help you explore this structure.

## Available Tools

### Extract Wikilinks

Fast extraction of all wikilinks from documents with line numbers and context.

**Use cases:**

- Finding all links in a document
- Understanding document structure
- Identifying referenced documents

**Example:**

```
You: What documents does my "Project Overview" link to?
AI: [Extracts and lists all wikilinks from the document]
```

### Find Backlinks

Discover what documents link TO a target document (reverse navigation).

**Use cases:**

- Finding documents that reference a specific note
- Understanding document importance
- Discovering unexpected connections

**Example:**

```
You: What documents link to "Machine Learning Basics"?
AI: [Lists all documents containing links to that document]
```

### Find Forward Links

Discover what documents a source document links TO (forward navigation).

**Use cases:**

- Following document references
- Understanding document dependencies
- Tracing idea development

**Example:**

```
You: What documents does "Research Notes" link to?
AI: [Lists all documents referenced from that document]
```

### Link Path Finding

Find connection paths between documents through wikilinks.

**Use cases:**

- Discovering how ideas connect
- Finding indirect relationships
- Understanding knowledge flow

**Example:**

```
You: How are "Concept A" and "Concept B" connected?
AI: [Finds paths: A → C → D → B, showing intermediate documents]
```

### Link Metrics

Analyze connectivity patterns and identify hub documents.

**Use cases:**

- Finding central/important documents
- Identifying isolated notes
- Understanding vault structure
- Discovering knowledge hubs

**Example:**

```
You: What are my most connected documents?
AI: [Lists documents with the most links, showing hub documents]
```

## Use Cases

### Knowledge Discovery

**Find Related Concepts:**

```
You: Find all documents connected to "Neural Networks" within 2 links
AI: [Shows network of related documents]
```

**Identify Knowledge Gaps:**

```
You: What documents have no incoming links?
AI: [Lists isolated documents that may need more integration]
```

### Navigation

**Follow Thought Trails:**

```
You: Show me the path from "Project Idea" to "Implementation"
AI: [Displays the connection path through intermediate notes]
```

**Explore Neighborhoods:**

```
You: What's around "Database Design"?
AI: [Shows incoming and outgoing links, creating a local graph view]
```

### Analysis

**Find Hub Documents:**

```
You: What are my most referenced documents?
AI: [Uses Link Metrics to identify central documents]
```

**Analyze Link Patterns:**

```
You: How well connected is my "Machine Learning" cluster?
AI: [Analyzes link density in that topic area]
```

### Maintenance

**Find Broken Links:**

```
You: Are there any wikilinks that don't resolve to documents?
AI: [Identifies broken links]
```

**Discover Orphaned Documents:**

```
You: What documents have no links in or out?
AI: [Lists completely isolated documents]
```

## Examples

### Research Workflow

```
You: What documents link to my literature review?
AI: [Shows backlinks - papers that cite this review]

You: What papers does my literature review cite?
AI: [Shows forward links - papers referenced in the review]

You: Find the most central papers in my research
AI: [Uses Link Metrics to identify hub papers]
```

### Writing Workflow

```
You: I'm writing about topic X. What related notes do I have?
AI: [Finds documents connected to X within 2-3 links]

You: Show me how these concepts connect
AI: [Uses Link Path Finding to show relationships]

You: Create an outline based on these connections
AI: [With --unsafe, generates an outline following the graph structure]
```

### Vault Maintenance

```
You: Find documents with broken links
AI: [Identifies wikilinks that don't resolve]

You: What documents are isolated?
AI: [Finds documents with no connections]

You: What are good candidates for linking?
AI: [Suggests documents that should be connected]
```

## Graph Visualization

While Zk-Chat doesn't provide visual graphs directly, you can:

1. Export link data
2. Use Obsidian's graph view
3. Use third-party graph tools

**Example:**

```
You: List all links between my "Projects" documents
AI: [Provides link data that can be visualized elsewhere]
```

## Best Practices

### Start with Hubs

Identify and explore hub documents first:

```
You: What are my 5 most connected documents?
```

### Use Incremental Exploration

Explore the graph step-by-step:

```
You: What links to "Concept A"?
AI: [Shows backlinks]

You: Tell me about [specific backlink]
AI: [Reads that document]

You: What does that link to?
AI: [Shows forward links, continuing exploration]
```

### Combine with Search

Use graph tools alongside search:

```
You: Find documents about "productivity"
AI: [Uses semantic search]

You: What do these documents link to?
AI: [Shows forward links, expanding the result set]
```

### Regular Analysis

Periodically analyze your graph:

```
You: What are my orphaned documents?
You: What are my hub documents?
You: What clusters exist in my vault?
```

## Limitations

- Link analysis is based on wikilinks only
- Performance depends on vault size
- Complex path finding can be slow for large vaults

## Next Steps

- [Document Management](document-management.md) - Work with documents
- [Git Integration](git-integration.md) - Version control
- [Interactive Chat](../user-guide/interactive-chat.md) - Using tools in conversation
