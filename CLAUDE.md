# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

zk-chat is a Python-based command-line and GUI tool for chatting with an AI that has access to your Zettelkasten (knowledge base). The project implements a RAG (Retrieval Augmented Generation) system that can search, read, and optionally modify markdown documents in a vault.

## Core Architecture

### Entry Points
The project provides four main command-line entry points (defined in `pyproject.toml`):
- `zkindex` - Document indexing (`zk_chat.index:main`)
- `zkchat` - Command-line chat interface (`zk_chat.chat:main`)
- `zkagent` - Agent-based interface (`zk_chat.agent:main`)
- `zkchat-gui` - Qt-based graphical interface (`zk_chat.qt:main`)

### Key Components

**Service Architecture**: The project uses a service registry pattern (`zk_chat/services/`) where plugins and tools access services through a `ServiceProvider`. This allows for extensible dependency injection without changing plugin constructors as new services are added.

**Plugin System**: Extensible plugin architecture via Python entry points in the `zk_rag_plugins` group. Plugins inherit from `ZkChatPlugin` base class and get access to all services through the service provider pattern.

**Vector Database**: Uses ChromaDB for semantic search with separate collections for documents and excerpts. The vector database is stored in `.zk_chat_db/` within each vault.

**LLM Integration**: Supports both Ollama (default) and OpenAI through the `mojentic` library. Model gateway selection is configurable.

**Zettelkasten Management**: Core `Zettelkasten` class handles document operations, indexing, and search. Supports markdown files with wikilink resolution.

**Memory System**: Smart Memory feature provides persistent context storage across chat sessions using vector embeddings.

### Tool Architecture

Built-in tools are located in `zk_chat/tools/` and include:
- Document operations (read, write, rename, delete, list)
- Search tools (find documents, find excerpts)
- Memory tools (store/retrieve from smart memory)
- Git integration (view changes, commit)
- Visual analysis (analyze images)
- Wikilink resolution

## Development Commands

### Testing
```bash
pytest                    # Run all tests (uses pytest-spec for readable output)
pytest zk_chat/          # Run tests from specific directory
```

The project uses pytest with specification-style output configuration. Test files follow the pattern `*_spec.py` and are located alongside the source files.

### Linting
```bash
flake8                    # Run linting (dev dependency)
```

### Dependencies
```bash
pip install -e .          # Install in development mode
pip install -e .[dev]     # Install with development dependencies
```

### Building
```bash
python -m build          # Build package for distribution
```

## Configuration

- **Vault Configuration**: Stored in `.zk_chat` file within each vault
- **Global Bookmarks**: Managed through command-line `--add-bookmark`/`--remove-bookmark` options
- **Database**: ChromaDB vector database stored in `.zk_chat_db/` within vault
- **System Prompt**: Customizable `ZkSystemPrompt.md` file in vault root

## Plugin Development

Plugins should inherit from `ZkChatPlugin` and use the service provider pattern:

```python
from zk_chat.services import ZkChatPlugin, ServiceProvider

class MyPlugin(ZkChatPlugin):
    def __init__(self, service_provider: ServiceProvider):
        super().__init__(service_provider)

    def run(self, input_text: str) -> str:
        # Access services via properties
        fs = self.filesystem_gateway
        zk = self.zettelkasten
        llm = self.llm_broker
        # Plugin logic here
        return result
```

Register plugins via entry points in `pyproject.toml`:
```toml
[project.entry-points]
zk_rag_plugins = { my_plugin = "my_plugin:MyPlugin" }
```

## Key Dependencies

- **mojentic**: LLM broker and gateway abstraction (>=0.6.1)
- **chromadb**: Vector database for semantic search (==0.6.3)
- **PySide6**: Qt-based GUI framework (>=6.6.0)
- **rich**: Terminal formatting and UI
- **pyyaml**: Configuration file parsing

## Testing Strategy

The project uses specification-style testing with files named `*_spec.py` alongside source files. Tests use pytest with readable output formatting and focus on behavior specifications rather than traditional unit tests.

## Git Integration

Optional git integration allows the AI to view uncommitted changes and create commits. Git operations are handled through the `GitGateway` service when enabled with the `--git` flag.