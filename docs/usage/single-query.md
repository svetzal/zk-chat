# Single Queries

For quick questions without starting a full interactive session, use the `query` command.

## Basic Usage

```bash
zk-chat query "What are my thoughts on productivity?"
```

## Reading from Standard Input

You can pipe questions from files or other commands:

```bash
# From a file
cat question.txt | zk-chat query

# From echo
echo "Summarize my machine learning notes" | zk-chat query

# From heredoc
zk-chat query << EOF
Find all documents about:
1. Neural networks
2. Deep learning
3. Computer vision
EOF
```

## Options

All the usual options are available:

```bash
# Use specific model
zk-chat query "..." --model qwen2.5:14b

# Use OpenAI
zk-chat query "..." --gateway openai

# Use agent mode for complex queries
zk-chat query "..." --agent

# Specify vault
zk-chat query "..." --vault /path/to/vault
```

## When to Use Queries vs Interactive

### Use Query Mode When:

- ✅ You have a single, specific question
- ✅ You want to script zk-chat usage
- ✅ You need quick one-off information
- ✅ You want to pipe output to other commands

### Use Interactive Mode When:

- ✅ You're exploring your vault
- ✅ You need follow-up questions
- ✅ You want to build on previous context
- ✅ You're doing deep research

## Examples

### Simple Question

```bash
zk-chat query "What is my GTD system?"
```

### Listing Documents

```bash
zk-chat query "List all documents about machine learning"
```

### Getting Summaries

```bash
zk-chat query "Summarize the key concepts in my productivity notes"
```

### Using Agent Mode

For complex queries that need planning:

```bash
zk-chat query "Find all connections between my deep work notes and flow state concepts, then explain the relationship" --agent
```

## Scripting with Queries

### Batch Processing

```bash
#!/bin/bash
# Process multiple questions

questions=(
    "What are my main productivity techniques?"
    "List recent machine learning concepts I've noted"
    "Summarize my thoughts on remote work"
)

for q in "${questions[@]}"; do
    echo "Question: $q"
    zk-chat query "$q"
    echo "---"
done
```

### Saving Output

```bash
# Save to file
zk-chat query "Summarize all my notes" > summary.txt

# Append to file
zk-chat query "List key concepts" >> concepts.txt
```

### Integration with Other Tools

```bash
# Use with grep
zk-chat query "List all productivity documents" | grep "GTD"

# Use with jq (if output is structured)
zk-chat query "..." | jq '.documents[]'

# Chain with other commands
zk-chat query "What did I write about today?" | mail -s "Daily Summary" me@example.com
```

## Tips

1. **Be Specific**: Single queries work best with specific questions
2. **Use Agent Mode Sparingly**: It's slower but handles complex queries better
3. **Test Interactively First**: Try your query in interactive mode first
4. **Consider Output Format**: Query output goes to stdout

## See Also

- [Interactive Chat](interactive-chat.md) - For extended conversations
- [Command Line Interface](cli.md) - Full CLI reference
