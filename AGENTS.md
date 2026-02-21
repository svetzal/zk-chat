# Project Guidance

## Project Overview

zk-chat is a Python-based command-line and GUI tool for chatting with an AI that has access to your Zettelkasten (knowledge base). The project implements a RAG (Retrieval Augmented Generation) system that can search, read, and optionally modify markdown documents in a vault.

## Core Architecture

### Entry Points

The project provides a single unified command-line entry point (`zk-chat`), defined in `pyproject.toml`.

The `zk-chat` CLI supports multiple modes and subcommands, including:
- Document indexing
- Command-line chat interface
- Agent-based operations
- Qt-based graphical interface

All functionality is accessible through the `zk-chat` command.

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

## Code Conventions

### Import Structure
Group imports in the following order, with one blank line between groups:
1. Standard library imports
2. Third-party library imports
3. Local application imports

Within each group, sort imports alphabetically.

### Naming Conventions
- Use descriptive variable names that indicate the purpose or content
- Prefix test mock objects with `mock_` (e.g., `mock_memory`)
- Prefix test data variables with `test_` (e.g., `test_query`)
- Use `_` for unused variables or return values

### Type Hints and Documentation
- Use type hints for method parameters and class dependencies
- Include return type hints when the return type isn't obvious
- Use docstrings for methods that aren't self-explanatory
- Class docstrings should describe the purpose and behavior of the component
- Follow numpy docstring style

### Logging
- Use structlog for all logging
- Initialize logger at module level using `logger = structlog.get_logger()`
- Include relevant context data in log messages
- Use appropriate log levels:
  - INFO for normal operations
  - DEBUG for detailed information
  - WARNING for concerning but non-critical issues
  - ERROR for critical issues
- Use print statements only for direct user feedback

### General Rules
- Do not write comments that just restate what the code does
- Use pydantic BaseModel classes, not `@dataclass`

## Testing

### General Rules
- Use pytest for all testing
- Test files are named with `_spec.py` suffix
- Test files are co-located with implementation files (same folder as the test subject)
- Run tests with: `pytest`
- Run linting with: `ruff check zk_chat`

### BDD-Style Tests

Follow a Behavior-Driven Development (BDD) style using the "Describe/should" pattern to make tests readable and focused on component behavior.

#### Test Structure
1. Tests are organized in classes that start with `Describe` followed by the component name
2. Test methods:
   - Start with `should_`
   - Describe the expected behavior in plain English
   - Follow the Arrange/Act/Assert pattern (separated by blank lines)
3. Do not use comments (e.g., Arrange, Act, Assert) to delineate test sections — just use a blank line
4. No conditional statements in tests — each test should fail for only one clear reason
5. Do not test private methods directly (those starting with `_`) — test through the public API

#### Fixtures and Mocking
- Use pytest `@fixture` for test prerequisites
  - Break large fixtures into smaller, reusable ones
  - Place fixtures in module scope for sharing between classes
  - Place module-level fixtures at the top of the file
- Mocking:
  - Use Mock with `spec` parameter for type safety (e.g., `Mock(spec=SmartMemory)`)
  - Only mock gateway classes; do not mock library internals or private functions

#### Best Practices
- Place instantiation/initialization tests first
- Group related scenarios together (success and failure cases)
- Keep tests focused on single behaviors
- One assertion per line for better error identification
- Use `in` operator for partial string matches
- Use `==` for exact matches
- Use fixtures for reusable prerequisites
- Define complex test data structures within test methods

#### Example

```python
class DescribeSmartMemory:
    """
    Tests for the SmartMemory component which handles memory operations
    """
    def should_be_instantiated_with_chroma_gateway(self):
        mock_chroma_gateway = Mock(spec=ChromaGateway)

        memory = SmartMemory(mock_chroma_gateway)

        assert isinstance(memory, SmartMemory)
        assert memory.chroma == mock_chroma_gateway
```

## Development Commands

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

## Key Dependencies

- **mojentic**: LLM broker and gateway abstraction (>=1.0.0)
- **chromadb**: Vector database for semantic search (>=1.3.0)
- **PySide6**: Qt-based GUI framework (>=6.8.0)
- **typer**: CLI framework with rich output support (>=0.20.0)
- **fastmcp**: Model Context Protocol support (>=2.0.0)
- **rich**: Terminal formatting and UI (>=14.0.0)
- **pyyaml**: Configuration file parsing (>=6.0.3)

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
   - Move items from "[Next]" section to new version section: `## [X.Y.Z] - YYYY-MM-DD`
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

- **Major Release (X.0.0)**: Breaking API changes, architectural changes, removal of deprecated features. Consider providing migration guides and highlighting breaking changes in the CHANGELOG.
- **Minor Release (0.X.0)**: New features, non-breaking enhancements, deprecation notices. Document new features and ensure backward compatibility.
- **Patch Release (0.0.X)**: Bug fixes, security updates, documentation corrections. Avoid introducing new features; maintain strict backward compatibility.
