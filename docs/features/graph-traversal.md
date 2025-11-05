# Graph Traversal

Graph traversal tools help you navigate and analyze the connections between documents in your Zettelkasten.

## Overview

Your Zettelkasten forms a knowledge graph where:
- **Nodes** = Documents
- **Edges** = Wikilinks between documents

Graph traversal tools help you explore this structure.

## Available Tools

### Extract Wikilinks

**Purpose:** Find all wikilinks in a document

**Example:**
```
You: What links are in "Getting Things Done"?

AI: Using tool: extract_wikilinks
Document: Getting Things Done.md

Found 5 wikilinks:
1. [[Next Actions]] (line 12)
2. [[Context Lists]] (line 24)
3. [[Weekly Review]] (line 45)
4. [[Project Planning]] (line 67)
5. [[Capture System]] (line 89)
```

### Find Backlinks

**Purpose:** Discover what documents link TO a target document

This answers: "What references this document?"

**Example:**
```
You: What documents link to "Getting Things Done"?

AI: Using tool: find_backlinks
Target: Getting Things Done.md

Found 5 documents with backlinks:
1. Daily Workflow.md (2 references)
2. Productivity System.md (1 reference)
3. Project Management.md (3 references)
4. Weekly Planning.md (1 reference)
5. Task Management.md (2 references)
```

### Find Forward Links

**Purpose:** Discover what documents a source document links TO

This answers: "What does this document reference?"

**Example:**
```
You: What does "Getting Things Done" link to?

AI: Using tool: find_forward_links
Source: Getting Things Done.md

Found 5 forward links:
1. Next Actions.md
2. Context Lists.md
3. Weekly Review.md
4. Project Planning.md
5. Capture System.md
```

### Link Path Finding

**Purpose:** Find connection paths between documents

This answers: "How are these concepts connected?"

**Example:**
```
You: How are "Deep Work" and "Flow State" connected?

AI: Using tool: link_path_finding
Source: Deep Work.md
Target: Flow State.md

Found 2 connection paths:

Path 1 (2 hops):
Deep Work → Focus Techniques → Flow State

Path 2 (2 hops):
Deep Work → Productivity Methods → Flow State
```

### Link Metrics

**Purpose:** Analyze connectivity and identify hub documents

**Example:**
```
You: What are my most connected documents?

AI: Using tool: link_metrics

Hub Documents (by total links):
1. Productivity System.md (45 links)
   - Incoming: 28
   - Outgoing: 17

2. Getting Things Done.md (32 links)
   - Incoming: 18
   - Outgoing: 14

3. Note-Taking Methods.md (29 links)
   - Incoming: 21
   - Outgoing: 8
```

## Use Cases

### Understanding Structure

**Find hub documents:**
```
You: What are my most important notes?

AI: [Uses link_metrics to identify highly connected documents]
```

### Discovering Connections

**Find relationships:**
```
You: How do my ideas about productivity relate to creativity?

AI: [Uses link_path_finding to discover connections]
```

### Navigation

**Explore related content:**
```
You: Show me what's related to this document

AI: [Uses find_backlinks and find_forward_links]
```

### Quality Assessment

**Check orphaned documents:**
```
You: What documents have no links?

AI: [Uses link_metrics to identify isolated documents]
```

## Graph Concepts

### Backlinks

**Definition:** Documents that link TO a target document

**Use:** Understanding what references a concept

**Example:**
```
Getting Things Done.md ← Daily Workflow.md
Getting Things Done.md ← Project Planning.md
```

### Forward Links

**Definition:** Documents that a source document links TO

**Use:** Understanding what a concept references

**Example:**
```
Getting Things Done.md → Next Actions.md
Getting Things Done.md → Context Lists.md
```

### Bidirectional Links

**Definition:** When two documents link to each other

**Significance:** Strong conceptual relationship

### Hub Documents

**Definition:** Documents with many links (in + out)

**Characteristics:**
- Central to your knowledge graph
- Connect many concepts
- Often important reference documents

### Orphaned Documents

**Definition:** Documents with no links

**Considerations:**
- May be new/incomplete
- May be independent topics
- May need integration

## Best Practices

### Using Wikilinks

**Good wikilinks:**
```markdown
The [[Getting Things Done]] system helps with [[Task Management]].
```

**Consistent naming:**
- Use the same title format
- Match actual document names
- Be consistent with capitalization

### Building Connections

1. **Link related concepts** - Connect similar ideas
2. **Create hub documents** - Build index/MOC pages
3. **Bidirectional linking** - Link back from referenced documents
4. **Semantic links** - Link based on meaning, not just keywords

### Analysis Workflow

```
1. Identify topic of interest
2. Find backlinks (what references it)
3. Find forward links (what it references)
4. Find paths to other concepts
5. Identify connection patterns
6. Build understanding
```

## Visualizing Connections

While zk-chat doesn't provide graph visualization, the tools help you:

- **Understand structure** - Through metrics and paths
- **Navigate effectively** - Following link chains
- **Discover patterns** - Identifying hubs and clusters

## Example Queries

### Discovery

```
"What are my most connected notes?"
"Show me hub documents"
"What links to this concept?"
```

### Navigation

```
"How do I get from [A] to [B]?"
"What connects these two ideas?"
"Show me the path between these documents"
```

### Analysis

```
"What documents have no links?"
"What's the structure of my productivity notes?"
"How interconnected is my vault?"
```

## Technical Details

### Wikilink Format

Supported formats:
```markdown
[[Document Name]]
[[Document Name|Display Text]]
[[folder/Document Name]]
```

### Path Finding Algorithm

- Uses breadth-first search
- Finds shortest paths
- Returns multiple paths if available
- Maximum depth configurable

### Performance

- Fast for small-medium vaults (<1000 docs)
- Scales well with vault size
- Results cached where appropriate

## See Also

- [Available Tools](tools.md) - All tool capabilities
- [Interactive Chat](../usage/interactive-chat.md) - Using tools in conversation
