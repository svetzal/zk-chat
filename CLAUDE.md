# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

zk-chat is a Python-based command-line and GUI tool for chatting with an AI that has access to your Zettelkasten (knowledge base). The project implements a RAG (Retrieval Augmented Generation) system that can search, read, and optionally modify markdown documents in a vault.

## Core Architecture

### Entry Points
The project now provides a single unified command-line entry point (`zk-chat`), defined in `pyproject.toml`.

The `zk-chat` CLI supports multiple modes and subcommands, including:
- Document indexing
- Command-line chat interface
- Agent-based operations
- Qt-based graphical interface

All functionality previously available via separate entry points is now accessible through the `zk-chat` command.
### Key Components

**Service Architecture**: The project uses a service registry pattern (`zk_chat/services/`) where plugins and tools access services through a `ServiceProvider`. This allows for extensible dependency injection without changing plugin constructors as new services are added.

**Plugin System**: Extensible plugin architecture via Python entry points in the `zk_rag_plugins` group. Plugins inherit from `ZkChatPlugin` base class and get access to all services through the service provider pattern.

**Vector Database**: Uses ChromaDB for semantic search with separate collections for documents and excerpts. The vector database is stored in `.zk_chat_db/` within each vault.

**LLM Integration**: Supports both Ollama (default) and OpenAI through the `mojentic` library. Model gateway selection is configurable.

**Zettelkasten Management**: Core `Zettelkasten` class handles document operations, indexing, and search. Supports markdown files with wikilink resolution.

**Memory System**: Smart Memory feature provides persistent context storage across chat sessions using vector embeddings.

### Tool Architecture

Built-in tools are located in `zk_chat/tools/` and include:
- **Document operations**: read, write, rename, delete, list
- **Search tools**: find documents, find excerpts
- **Graph traversal**: extract wikilinks, find backlinks/forward links, link path finding
- **Memory tools**: store/retrieve from smart memory
- **Git integration**: view changes, commit (requires `--git` flag)
- **Visual analysis**: analyze images (requires visual model)
- **Wikilink resolution**: convert wikilinks to file paths

### MCP Integration

The project supports Model Context Protocol (MCP) for external tool integration:
- **MCP Client**: `zk_chat/mcp_client.py` handles communication with MCP servers
- **MCP Tool Wrapper**: `zk_chat/mcp_tool_wrapper.py` wraps MCP tools as LLM tools
- **MCP Commands**: `zk-chat mcp` CLI commands for server registration and management
- **Server Types**: Supports both STDIO and HTTP MCP servers
- MCP tools are automatically loaded and verified before chat/agent sessions

## Development Commands

### Testing
```bash
pytest                    # Run all tests (uses pytest-spec for readable output)
pytest zk_chat/          # Run tests from specific directory
```

The project uses pytest with specification-style output configuration. Test files follow the pattern `*_spec.py` and are co-located alongside the source files they test.

**Test Style**: BDD-style tests using the "Describe/should" pattern:
- Test classes start with `Describe` followed by component name
- Test methods start with `should_` and describe expected behavior
- Follow Arrange/Act/Assert pattern separated by blank lines (no comments)
- Use pytest fixtures for test prerequisites; prefix mocks with `mock_`
- Only mock gateway classes; don't mock library internals
- Use Mock with spec parameter for type safety (e.g., `Mock(spec=SmartMemory)`)

### Linting
```bash
# Ruff uses configuration from pyproject.toml (line length 120, max complexity 10)
ruff check zk_chat
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

### Diagnostics
```bash
zk-chat diagnose index              # Check index health and collection status
zk-chat diagnose index --query "test"  # Run test query to verify search is working
```

The diagnostic command helps troubleshoot indexing and search issues by:
- Checking ChromaDB collection existence and document counts
- Showing sample documents from each collection
- Testing embedding generation
- Running test queries to verify search functionality

## Configuration

- **Vault Configuration**: Stored in `.zk_chat` file within each vault
- **Global Bookmarks**: Managed through `GlobalConfig` stored in `~/.zk_chat`. Both CLI and GUI share this bookmark system
- **Database**: ChromaDB vector database stored in `.zk_chat_db/` within vault
- **System Prompt**: Customizable `ZkSystemPrompt.md` file in vault root

### GUI Configuration
The Qt GUI uses the same configuration system as the CLI:
- On first launch, it loads the last opened bookmark from `GlobalConfig`
- If no bookmark exists, prompts the user to select a vault directory
- Vault changes through the GUI settings dialog automatically update global bookmarks
- Model and gateway settings are shared with the CLI for the same vault

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

## Code Conventions

### General Guidelines
- **Imports**: Group in order (standard library, third-party, local) with blank line between groups, sorted alphabetically within groups
- **Type Hints**: Use type hints for method parameters and class dependencies; include return types when not obvious
- **Documentation**: Use numpy docstring style; document non-obvious methods and all classes
- **Logging**: Use structlog for all logging; initialize with `logger = structlog.get_logger()` at module level
- **Data Classes**: Use pydantic BaseModel classes, not @dataclass
- **Naming**: Use descriptive names; prefix test mocks with `mock_`, test data with `test_`

## Key Dependencies

- **mojentic**: LLM broker and gateway abstraction (>=0.8.2)
- **chromadb**: Vector database for semantic search (>=1.1.0)
- **PySide6**: Qt-based GUI framework (>=6.6.0)
- **typer**: CLI framework with rich output support (>=0.9.0)
- **fastmcp**: Model Context Protocol support (>=2.0.0)
- **rich**: Terminal formatting and UI
- **pyyaml**: Configuration file parsing

## Testing Strategy

The project uses specification-style testing with files named `*_spec.py` alongside source files. Tests use pytest with readable output formatting and focus on behavior specifications rather than traditional unit tests.

## Git Integration

Optional git integration allows the AI to view uncommitted changes and create commits. Git operations are handled through the `GitGateway` service when enabled with the `--git` flag.

## Release Process

This project follows [Semantic Versioning](https://semver.org/) (SemVer) for version numbering. The version format is MAJOR.MINOR.PATCH.

### Release Checklist

Follow these steps in order when preparing and publishing a release:

1. **Verification Phase**:
   ```bash
   # All lint checks must pass
   ruff check zk_chat

   # All unit tests must pass
   pytest zk_chat/

   # All integration tests must pass
   pytest integration_tests/
   ```

2. **Documentation Phase**:
   - Ensure CHANGELOG.md is up to date with all changes for this release
   - Verify README.md reflects current features and version
   - Ensure all documentation in docs/ is current
   - Update version in pyproject.toml

3. **Commit and Push**:
   ```bash
   # Commit release changes
   git add pyproject.toml CHANGELOG.md README.md docs/
   git commit -m "Release vX.Y.Z with [brief description]"

   # Push to trigger CI/CD validation
   git push
   ```

4. **Monitor Build**:
   ```bash
   # Monitor the GitHub Actions workflow
   gh run watch

   # Wait for green build before proceeding
   # If build fails, fix issues and repeat from step 1
   ```

5. **Tag Release**:
   ```bash
   # Create tag in format RELEASE_MAJOR_MINOR_PATCH
   # Example: for version 3.5.0, tag is RELEASE_3_5_0
   git tag RELEASE_X_Y_Z

   # Push the tag to trigger release workflow
   git push origin RELEASE_X_Y_Z
   ```

6. **Monitor Release Build**:
   ```bash
   # Watch the release workflow
   gh run watch

   # Verify:
   # - Documentation deployed to GitHub Pages
   # - Package published to PyPI
   ```

7. **Create GitHub Release**:
   ```bash
   # Create release with content from CHANGELOG
   gh release create RELEASE_X_Y_Z \
     --title "vX.Y.Z - [Brief Title]" \
     --notes "$(sed -n '/## \[X.Y.Z\]/,/## \[/p' CHANGELOG.md | head -n -1)"

   # Or create interactively to edit release notes
   gh release create RELEASE_X_Y_Z --draft --generate-notes
   ```

### Release Types

- **Major Release (X.0.0)**: Breaking API changes, architectural changes
- **Minor Release (0.X.0)**: New features, non-breaking enhancements
- **Patch Release (0.0.X)**: Bug fixes, security updates, documentation fixes