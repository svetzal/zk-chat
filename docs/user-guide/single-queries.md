# Single Queries

Sometimes you don't need an interactive chat session - you just want to ask a single question and get an answer. That's what the `query` command is for.

## Basic Usage

```bash
zk-chat query "What are my thoughts on productivity?"
```

The AI will:

1. Search your Zettelkasten for relevant documents
2. Read and analyze relevant content
3. Provide a single response
4. Exit

## Reading from Standard Input

You can pipe questions from files or other commands:

```bash
# From a file
cat prompt.txt | zk-chat query

# From echo
echo "What are my notes about machine learning?" | zk-chat query

# From heredoc
zk-chat query << EOF
Please summarize my notes about:
- Machine learning
- Deep learning
- Neural networks
EOF
```

## Options

### Specify Vault

```bash
zk-chat query "What are my thoughts on leadership?" --vault /path/to/vault
```

### Use Different Model

```bash
zk-chat query "Analyze my project notes" --model qwen2.5:14b
```

### Use Agent Mode

For complex queries that require multi-step reasoning:

```bash
zk-chat query "Find all related concepts to topic X" --agent
```

### Use OpenAI

```bash
zk-chat query "What are my ideas about startups?" --gateway openai --model gpt-4
```

## Use Cases

### Quick Information Retrieval

```bash
zk-chat query "What is the definition of X in my notes?"
```

### Scripting and Automation

Use in scripts to extract information:

```bash
#!/bin/bash
# Generate a daily summary

summary=$(zk-chat query "Summarize documents modified in the last 24 hours")
echo "$summary" > daily-summary.txt
```

### Batch Processing

Process multiple queries:

```bash
# queries.txt contains one query per line
while IFS= read -r query; do
    echo "Query: $query"
    zk-chat query "$query"
    echo "---"
done < queries.txt
```

### Integration with Other Tools

```bash
# Combine with grep, awk, etc.
zk-chat query "List all project names" | grep -i "active"

# Generate reports
zk-chat query "Monthly summary" > reports/$(date +%Y-%m).txt
```

## Query Best Practices

### Be Specific

Good:

```bash
zk-chat query "What are the three main themes in my leadership notes?"
```

Less good:

```bash
zk-chat query "Tell me about leadership"
```

### Single Purpose

Each query should have a single, clear purpose:

```bash
# Good - single purpose
zk-chat query "List all documents about Python"

# Less ideal - multiple purposes (better as separate queries)
zk-chat query "List all documents about Python and summarize each one and create a new document"
```

For complex multi-step tasks, use agent mode or interactive chat.

### Structured Output Requests

You can request structured output:

```bash
zk-chat query "List my top 5 project ideas in bullet points"

zk-chat query "Create a table of all people mentioned in my meeting notes"
```

## Differences from Interactive Chat

| Feature | Interactive Chat | Single Query |
|---------|-----------------|--------------|
| Session | Multi-turn conversation | Single question-answer |
| Context | Maintains conversation history | No conversation history |
| Speed | Initial indexing, then fast | Same speed for each query |
| Use Case | Exploration, complex tasks | Quick info retrieval, scripting |
| Tool Usage | Full tool access | Full tool access |
| Agent Mode | Available | Available |

## Performance Considerations

### Index State

The query command uses the existing index. If your vault has changed significantly:

```bash
# Rebuild index first
zk-chat index rebuild

# Then run query
zk-chat query "Your question"
```

### Model Selection

- **Faster models**: `phi4:14b`, smaller parameter models
- **More capable**: `qwen2.5:14b`, `qwq:32b`

Choose based on your needs:

- Quick facts: Use faster models
- Complex analysis: Use more capable models

## Examples

### Research

```bash
# Find information
zk-chat query "What experiments did I document about topic X?"

# Get definitions
zk-chat query "How do I define 'zettelkasten' in my notes?"

# Find connections
zk-chat query "What connections exist between concept A and concept B?"
```

### Writing Support

```bash
# Get relevant context
zk-chat query "What have I written about character development?"

# Find examples
zk-chat query "Find examples of dialogue in my writing notes"
```

### Project Management

```bash
# Status check
zk-chat query "What are my active projects?"

# Task extraction
zk-chat query "List all pending tasks from project notes"
```

### Knowledge Discovery

```bash
# Find gaps
zk-chat query "What topics have I mentioned but not explored in depth?"

# Identify patterns
zk-chat query "What are recurring themes in my daily notes?"
```

## Advanced Usage

### Complex Agent Queries

Use agent mode for multi-step analysis:

```bash
zk-chat query "Analyze all documents about machine learning, identify the main topics, and rank them by how much I've written about each" --agent
```

### Output Formatting

Request specific formats:

```bash
# Markdown format
zk-chat query "Create a markdown outline of my project notes"

# JSON-like output
zk-chat query "List all tags used in my notes as a simple list"
```

## Troubleshooting

### No Results Found

- Verify vault path: `--vault /path/to/vault`
- Check index status: `zk-chat index status`
- Rebuild index: `zk-chat index rebuild`

### Unexpected Results

- Be more specific in your query
- Try rephrasing the question
- Use agent mode for complex queries

### Performance Issues

- Use a smaller/faster model
- Ensure index is up to date
- Check available system resources

## Next Steps

- [Interactive Chat](interactive-chat.md) - For multi-turn conversations
- [Index Management](index-management.md) - Keep your index optimized
- [CLI Reference](../reference/cli-commands.md) - All command options
