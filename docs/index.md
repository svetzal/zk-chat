# Welcome to zk-chat

zk-chat is a powerful command-line tool that lets you chat with an AI assistant that has access to your Zettelkasten (knowledge base). It indexes your markdown documents and provides intelligent search, retrieval, and analysis capabilities.

## What is zk-chat?

zk-chat combines the power of modern AI language models with your personal knowledge base. Whether you use Obsidian, Logseq, or any markdown-based note-taking system, zk-chat can help you:

- **Find relevant information** quickly using semantic search
- **Extract insights** from your notes through AI analysis
- **Navigate connections** between ideas using wikilink traversal
- **Enhance your notes** with AI-powered writing assistance
- **Visualize patterns** across your knowledge base

## Key Features

### 🔍 Intelligent Search
Search your Zettelkasten using natural language queries. The AI understands context and meaning, not just keywords.

### 🛠️ Rich Tool Ecosystem
Access a comprehensive set of built-in tools for document management, graph traversal, visual analysis, and more. Extend functionality with custom plugins.

### 🧠 Smart Memory
The AI remembers important context across chat sessions, providing increasingly personalized and contextual responses.

### 🔌 Extensible Architecture
Create custom plugins to add new capabilities, or integrate external tools via the Model Context Protocol (MCP).

### 💻 Multiple Interfaces
Use the command-line interface for quick queries, or launch the experimental GUI for a more visual experience.

## Quick Example

```bash
# Start an interactive chat session
zk-chat interactive --vault /path/to/your/vault

# Ask a single question
zk-chat query "What are my thoughts on productivity?"

# Use agent mode for complex tasks
zk-chat interactive --agent --unsafe --git
```

## Getting Started

Ready to dive in? Check out the [Installation Guide](installation.md) to get started, or explore the [Quick Start](quick-start.md) tutorial for a guided introduction.

## Community and Support

- **GitHub**: [svetzal/zk-chat](https://github.com/svetzal/zk-chat)
- **Issues**: [Report bugs or request features](https://github.com/svetzal/zk-chat/issues)
- **Discussions**: [Ask questions and share ideas](https://github.com/svetzal/zk-chat/discussions)

## License

zk-chat is open source software licensed under the MIT License.
