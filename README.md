# 💬 zk-chat: AI-Powered Chat for Your Zettelkasten

**Transform your Zettelkasten into an intelligent knowledge assistant.** zk-chat lets you have natural conversations with your notes using AI—whether you run models locally with Ollama or use OpenAI's cloud API.

[![PyPI](https://img.shields.io/pypi/v/zk-chat)](https://pypi.org/project/zk-chat/)
[![Python Version](https://img.shields.io/pypi/pyversions/zk-chat)](https://pypi.org/project/zk-chat/)
[![Documentation](https://img.shields.io/badge/docs-vetzal.com-blue)](https://vetzal.com/zk-chat/)
[![License](https://img.shields.io/github/license/svetzal/zk-chat)](https://github.com/svetzal/zk-chat/blob/main/LICENSE)

## 🎯 Why zk-chat?

- **🔒 Privacy First**: Run everything locally with Ollama—no data leaves your machine
- **🤖 AI-Powered RAG**: Semantic search with vector embeddings finds exactly what you need
- **📊 Visual Analysis**: Analyze diagrams, charts, and images in your notes
- **🔗 Graph Traversal**: Discover connections through wikilinks, backlinks, and forward links
- **🧠 Smart Memory**: AI remembers context across conversations
- **🔌 Extensible**: MCP server support and plugin architecture
- **⚡ Fast**: Efficient local indexing and incremental updates
- **💻 CLI & GUI**: Choose your interface—powerful command-line or experimental GUI

## 📚 Documentation

**Full documentation:** [https://vetzal.com/zk-chat/](https://vetzal.com/zk-chat/)

- [Installation Guide](https://vetzal.com/zk-chat/installation/) - Get started in minutes
- [Quick Start Tutorial](https://vetzal.com/zk-chat/quick-start/) - Your first conversation
- [Model Selection Guide](https://vetzal.com/zk-chat/configuration/models/) - Choose the right model for your hardware
- [Command Reference](https://vetzal.com/zk-chat/usage/cli/) - Complete CLI documentation
- [Plugin Development](https://vetzal.com/zk-chat/plugins/guide/) - Extend zk-chat with custom tools

## 🚀 Quick Start

### Installation

```bash
# Install with pipx (recommended)
pipx install zk-chat

# Install Ollama and a model
brew install ollama
ollama pull qwen3:8b

# For visual analysis (optional)
ollama pull gemma3:27b
```

### Your First Chat

```bash
# Start interactive session
zk-chat interactive --vault /path/to/your/notes

# Ask a question
zk-chat query "What are my main ideas about productivity?"

# Single query with visual model
zk-chat query "Analyze diagram.png" --visual-model gemma3:27b
```

## ✨ Key Features

### 🔍 Intelligent Search & Retrieval
- **Semantic Search**: Vector embeddings find conceptually similar content
- **Excerpt Retrieval**: Extract relevant passages from your documents
- **Full Document Access**: AI can read complete notes when needed
- **Graph Traversal**: Explore connections via wikilinks, backlinks, and forward links
- **Link Path Finding**: Discover how concepts connect through your knowledge graph

### 🤖 AI Capabilities
- **RAG (Retrieval Augmented Generation)**: AI answers using your actual notes
- **Smart Memory**: Persistent context across conversations
- **Visual Analysis**: Understand diagrams, charts, and images
- **Multi-Model Support**: Choose from dozens of Ollama models or use OpenAI
- **Autonomous Agent Mode**: AI can plan and execute complex multi-step tasks

### 🛠️ Content Management
- **Read-Only by Default**: Safe exploration of your knowledge base
- **Optional Writing**: Enable `--unsafe` mode for AI-assisted content creation
- **Git Integration**: Track all AI changes with automatic commits
- **Wikilink Support**: Full understanding of `[[wikilink]]` syntax
- **Markdown Native**: Works seamlessly with Obsidian and other markdown tools

### 🔌 Extensibility
- **MCP Server Support**: Connect external tools via Model Context Protocol
- **Plugin Architecture**: Extend with custom Python plugins
- **Available Plugins**:
  - [Wikipedia Integration](https://pypi.org/project/zk-rag-wikipedia/) - Research and create notes from Wikipedia
  - [Image Generation](https://pypi.org/project/zk-rag-image-generator/) - Generate images with Stable Diffusion 3.5

## 📦 What's New in v3.5.0

### 🔖 Bookmark Management
```bash
# List all vault bookmarks
zk-chat bookmarks list

# Remove a bookmark
zk-chat bookmarks remove /path/to/vault
```

### 🔍 Index Diagnostics
```bash
# Check index health
zk-chat diagnose index

# Run test query to verify search
zk-chat diagnose index --query "test"
```

### 🔌 MCP Server Integration
```bash
# Register external tools
zk-chat mcp register figma stdio "figma-mcp"

# List and verify servers
zk-chat mcp list
zk-chat mcp verify
```

### 🤖 Updated Model Recommendations (2025)

**Choose based on your RAM:**

| RAM Available | Text Model | Visual Model |
|---------------|------------|--------------|
| **64GB+** | `gpt-oss:120b`, `qwen3:32b` | `gemma3:27b` |
| **36-48GB** | `gpt-oss:20b`, `qwen3:14b` | `gemma3:27b` |
| **16-32GB** | `qwen3:8b`, `qwen2.5:7b` | `gemma3:9b` |
| **8-16GB** | `qwen3:1.5b`, `qwen2.5:3b` | `gemma3:2b` |

See the [Model Selection Guide](https://vetzal.com/zk-chat/configuration/models/) for detailed recommendations by task and hardware.

## 💡 Usage Examples

### Interactive Chat
```bash
# Start a conversation
zk-chat interactive

# With specific model
zk-chat interactive --model qwen3:14b

# Allow AI to edit files (with git tracking)
zk-chat interactive --unsafe --git

# With visual analysis
zk-chat interactive --visual-model gemma3:27b
```

### Single Queries
```bash
# Direct question
zk-chat query "What are my thoughts on AI?"

# From file or stdin
cat question.txt | zk-chat query

# Complex multi-step query
zk-chat query "Find all notes about productivity and create a summary"
```

### Bookmark Management
```bash
# Save current vault
zk-chat interactive --vault ~/notes --save

# List bookmarks
zk-chat bookmarks list

# Remove bookmark
zk-chat bookmarks remove ~/old-notes
```

### Index Management
```bash
# Quick incremental update
zk-chat index update

# Full rebuild
zk-chat index update --full

# Check status
zk-chat index status
```

### Visual Analysis
Ask natural questions about images in your vault:
- "What's in the diagram at architecture.png?"
- "Describe the chart in sales-data.jpg"
- "Extract text from screenshot.png"

## 🎛️ Command-Line Options

### Common Options (All Commands)
- `--vault PATH` or `-v` - Path to your Zettelkasten
- `--gateway {ollama,openai}` or `-g` - Choose AI provider
- `--model NAME` or `-m` - Specify chat model
- `--visual-model NAME` - Specify visual analysis model
- `--save` - Bookmark the current vault
- `--no-index` - Skip indexing on startup (faster start)

### Agent Mode Options
- `--unsafe` - Allow AI to create/edit files ⚠️
- `--git` - Enable git integration (recommended with --unsafe)
- `--store-prompt` / `--no-store-prompt` - Control system prompt storage
- `--reset-memory` - Clear smart memory

> **⚠️ Safety:** The `--unsafe` flag allows AI to modify your notes. Always use with `--git` for tracking changes.

## 🔧 Requirements

### For Local AI (Ollama)
- [Ollama](https://ollama.com/) installed and running
- Sufficient RAM for your chosen model (8GB minimum, 16GB+ recommended)
- Compatible with macOS (M1/M2/M3 recommended), Linux, and Windows

### For Cloud AI (OpenAI)
- OpenAI API key set in `OPENAI_API_KEY` environment variable
- Internet connection
- API credits

### Your Zettelkasten
- Markdown notes (`.md` files)
- Works with Obsidian, Logseq, or any markdown-based system
- Supports wikilinks (`[[Note Name]]`)

## 🏗️ Architecture

zk-chat uses a modern RAG architecture:

1. **Indexing**: Creates vector embeddings of your notes using ChromaDB
2. **Retrieval**: Semantic search finds relevant content for queries
3. **Generation**: LLM generates responses using retrieved context
4. **Tools**: AI can use 15+ tools to explore and interact with your vault

The AI agent has access to:
- Document search and retrieval
- Wikilink graph traversal
- Visual analysis (with vision models)
- Smart memory storage
- Git version control
- External tools via MCP servers

## 🔌 Plugin Development

Create custom tools for your specific needs:

```python
from zk_chat.services import ZkChatPlugin, ServiceProvider

class MyPlugin(ZkChatPlugin):
    def __init__(self, service_provider: ServiceProvider):
        super().__init__(service_provider)

    def run(self, input_text: str) -> str:
        # Access zk-chat services
        fs = self.filesystem_gateway
        zk = self.zettelkasten
        llm = self.llm_broker

        # Your plugin logic
        return result
```

See the [Plugin Development Guide](https://vetzal.com/zk-chat/plugins/guide/) for complete documentation.

## 📊 Performance Tips

### For Faster Responses
- Use smaller models (qwen3:1.5b, qwen2.5:3b)
- Increase concurrency: `export OLLAMA_NUM_PARALLEL=4`
- Skip indexing on startup: `--no-index`

### For Better Quality
- Use larger models (gpt-oss:20b, qwen3:14b)
- Increase context window: `export OLLAMA_NUM_CTX=16384`
- Enable visual analysis for image-heavy vaults

### Resource Management
```bash
# Check running models
ollama ps

# Monitor system resources
htop  # or Activity Monitor on Mac

# Remove unused models
ollama list
ollama rm unused-model
```

## 🗂️ Storage

zk-chat stores its data in your vault:
- `.zk_chat` - Configuration file
- `.zk_chat_db/` - Vector database (ChromaDB)
- `ZkSystemPrompt.md` - System prompt (customizable)

Add these to `.gitignore`:
```
.zk_chat_db/
.zk_chat
```

## 🆘 Troubleshooting

### Ollama Connection Issues
```bash
# Start Ollama
ollama serve

# Verify model installed
ollama list
```

### Index Problems
```bash
# Diagnose index health
zk-chat diagnose index

# Force full rebuild
zk-chat index update --full
```

### Performance Issues
- Try a smaller model
- Close other applications
- Increase system resources
- Use OpenAI instead of local models

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License

[MIT License](LICENSE) - Copyright (c) 2024-2025 Stacey Vetzal

## 🔗 Links

- **Documentation**: https://vetzal.com/zk-chat/
- **PyPI**: https://pypi.org/project/zk-chat/
- **GitHub**: https://github.com/svetzal/zk-chat
- **Issues**: https://github.com/svetzal/zk-chat/issues
- **Discussions**: https://github.com/svetzal/zk-chat/discussions

## ⭐ Star History

If you find zk-chat useful, please consider starring the repository on GitHub!

---

**Made with ❤️ for the Zettelkasten community**


## 🧹 Linting and Auto-fixing

This project uses Ruff for linting and auto-fixes (including removing unused imports/variables and sorting imports).

### Install dev tools

```bash
python -m pip install -e ".[dev]"
```

### Check for issues (no changes written)

```bash
# Lint with Ruff (fails on errors; uses pyproject.toml configuration)
ruff check zk_chat
```

### Auto-fix common issues (writes changes)

```bash
# Apply safe fixes (remove unused imports/variables, sort imports, etc.)
ruff check zk_chat --fix
```

Optional formatting (if desired):
```bash
# Ruff can also format code
ruff format zk_chat
```

Notes:
- Line length is enforced at 120 characters via Ruff (`pyproject.toml`).
- CI runs Ruff in the validation workflow; Flake8 and Autoflake are no longer used.
