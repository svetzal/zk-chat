# 💬 Chat With Your Zettelkasten

Welcome to Zk-Chat, a command-line tool that lets you chat with an "AI" that has access to the documents in your Zettelkasten. It will index your markdown documents, and in your chat session it may choose to query your content, retrieve excerpts, read entire documents, and generate responses based on the content in your Zettelkasten.

## What is Zk-Chat?

Zk-Chat is a powerful tool that combines the benefits of:

- **Personal Knowledge Management**: Works with your Zettelkasten (like Obsidian vaults)
- **AI-Powered Chat**: Uses LLMs (via Ollama or OpenAI) to understand and respond to your queries
- **RAG (Retrieval Augmented Generation)**: Queries your documents to provide context-aware responses
- **Extensible Architecture**: Supports plugins for additional capabilities

## Key Features

- ✅ **Command-line interface** for quick access
- ✅ **Graphical user interface** (experimental) for a more user-friendly experience
- ✅ **RAG queries** across your document base
- ✅ **Interactive chat** with context from your Zettelkasten
- ✅ **Configurable LLM models** - use Ollama or OpenAI
- ✅ **Visual analysis** capability for images in your Zettelkasten
- ✅ **Easy Zettelkasten folder configuration**
- ✅ **Plugin system** for extending functionality
- ✅ **Smart memory** for long-term context retention
- ✅ **Git integration** for version control
- ✅ **MCP (Model Context Protocol)** server support

## Quick Start

Get started with Zk-Chat in minutes:

1. **Install**: `pipx install zk-chat`
2. **Setup**: Ensure Ollama is running (or set up OpenAI API key)
3. **Chat**: `zk-chat interactive --vault /path/to/vault`

For detailed installation instructions, see [Getting Started](getting-started/installation.md).

## Use Cases

Zk-Chat is perfect for:

- 📚 **Research**: Query your research notes and literature
- 📝 **Writing**: Get context from your knowledge base while writing
- 🔍 **Discovery**: Find connections between ideas in your notes
- 🤖 **Automation**: Use agent mode for complex multi-step tasks
- 🎨 **Creativity**: Generate ideas based on your existing knowledge

## Architecture

Zk-Chat is built on top of [Mojentic](https://github.com/svetzal/mojentic), an agentic framework that provides:

- LLM abstraction layer (supports multiple providers)
- Tool-based agent architecture
- Event-driven asynchronous processing
- Structured output capabilities

## Documentation Overview

- **[Getting Started](getting-started/installation.md)**: Installation and initial setup
- **[User Guide](user-guide/interactive-chat.md)**: How to use Zk-Chat features
- **[Tools](tools/document-management.md)**: Available tools and capabilities
- **[Plugin Development](plugins/overview.md)**: Create custom plugins
- **[Reference](reference/cli-commands.md)**: CLI commands and configuration

## Community

- **GitHub**: [svetzal/zk-chat](https://github.com/svetzal/zk-chat)
- **Issues**: Report bugs and request features
- **Plugins**: Check out available plugins on PyPI

## License

Zk-Chat is open source software licensed under the MIT License.
