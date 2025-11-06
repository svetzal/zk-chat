# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Next]

## [3.5.0] - 2025-11-05

### Added

- **MCP Server Management**: Added comprehensive support for managing Model Context Protocol (MCP) server connections
  - New `zk-chat mcp` commands to register, list, remove, and verify MCP servers
  - Support for both STDIO and HTTP MCP server types
  - Automatic server availability verification before entering chat/agent sessions
  - Persistent storage of MCP server configurations in global config
  - Rich CLI output with table formatting for server listings
  - Validation of server configurations with helpful error messages
- **MCP Tool Integration**: Added wrapper to integrate external MCP server tools
  - `MCPToolWrapper` class that adapts MCP tools to mojentic `LLMTool` interface
  - Automatic discovery of all tools from registered MCP servers
  - Async/sync conversion for tool execution
  - Connection lifecycle management per tool
  - FastMCP library integration for MCP client functionality
- **Bookmarks Management**: New `zk-chat bookmarks` command for vault bookmark management
  - `zk-chat bookmarks list` - Display all bookmarked vaults with last opened indicator
  - `zk-chat bookmarks remove <path>` - Remove vault bookmarks
  - Removed bookmark management flags from interactive/query commands for cleaner CLI
- **Documentation Site**: Complete MkDocs-based documentation site
  - Comprehensive guides for installation, configuration, and usage
  - Feature documentation for all tools and capabilities
  - Plugin development guide
  - Deployed to GitHub Pages via automated workflow
- **Index Diagnostics**: New `zk-chat diagnose` command for troubleshooting
  - Check index health and collection status
  - Run test queries to verify search functionality
  - Display sample documents and index statistics
- **Unified CI/CD Workflow**: Consolidated GitHub Actions into single workflow
  - Combined build, test, and publish into `validate-test-publish.yml`
  - Added GitHub Pages deployment for documentation
  - Virtual environment caching for faster CI runs
  - Test coverage artifacts and JUnit XML reports

### Changed

- **CLI Command Structure**: Improved command organization and consistency
  - Unified parameters between `interactive` and `query` commands
  - Both commands now support `--save`, `--unsafe`, `--git`, `--store-prompt`, `--reset-memory`
  - Consistent `--visual-model` flag across all commands
  - Removed obsolete `--agent` flag from integration tests
- **Model Recommendations**: Updated documentation with 2025 Ollama model recommendations
  - Primary recommendations now favor qwen3, gpt-oss, and gemma3
  - Added comprehensive visual model guidance (gemma3, qwen3-vl, llama3.2-vision)
  - Updated default models: qwen3:8b (text), gemma3:27b (vision)
  - Tiered recommendations by RAM (64GB+, 36-48GB, 16-32GB, 8-16GB)
  - Detailed performance characteristics and use case guidance
- **Integration Testing**: Enhanced test harness with visual model support
  - Separate configuration for text and visual models
  - Environment variables: `ZK_TEST_MODEL`, `ZK_TEST_VISUAL_MODEL`
  - Updated defaults: qwen3:8b (text), gemma3:27b (vision)
  - Automatic model passing to CLI via `--visual-model` flag

### Fixed

- **Document Not Found**: Fixed crash when indexed document doesn't exist on filesystem
  - Added proper error handling in `read_document` method
  - Returns empty string instead of crashing when file not found
  - Improved error messages for missing documents

## [3.2.2] - 2025-09-29

### Changed

- **Updated mojentic dependency**: Bumped to version 0.8.2 for enhanced reasoning model support
  - Improved compatibility with advanced reasoning models like o1-preview and o1-mini
  - Better temperature handling and response parsing for reasoning-focused workflows
- **Improved model compatibility**: Changed default temperature settings for chat sessions to accommodate different model types, especially reasoning models

## [3.2.1] - 2025-09-28

### Changed

- **Updated mojentic dependency**: Ensured compatibility with version 0.8.0 for reasoning model support
  - Supports o1-preview, o1-mini, and other reasoning-focused LLM models
  - Better handling of reasoning model response patterns and token usage

## [3.2.0] - 2025-09-28

### Added

- **Graph Traversal Tools**: New suite of fast, local wikilink analysis tools
  - `ExtractWikilinksFromDocument`: Extract all wikilinks from documents with line numbers and context
  - `FindBacklinks`: Discover what documents link TO a target document
  - `FindForwardLinks`: Discover what documents a source document links TO
- **LinkTraversalService**: New compositional service architecture for wikilink operations
  - In-memory graph indexing with LinkGraphIndex for fast path finding
  - Support for backlink/forward link discovery with caching
  - Link path finding between documents with configurable hop limits
  - Link metrics calculation for connectivity analysis
- **Comprehensive Test Coverage**: 25+ BDD-style tests covering all graph traversal functionality
- **Performance Optimizations**: Zero-token graph operations using pure text parsing

### Changed

- **Compositional Architecture**: Moved from monolithic design toward specialized services
- **Tool Integration**: All graph traversal tools integrated into agent with proper LLM descriptors

### Fixed

- **JSON Serialization**: Fixed datetime serialization errors in `find_zk_documents_related_to` and `find_excerpts_related_to` tools
- **Test Suite**: Updated ExtractWikilinksFromDocument tests to work with new LinkTraversalService architecture
- **Mock Configuration**: Corrected test mocks to properly simulate filesystem gateway interactions

## [3.1.0] - 2025-09-28

### Added

- Enhanced CLI structure with refactored command organization

### Fixed

- Updated max_distance handling in query_excerpts method for improved query accuracy
- Resolved ChromaDB telemetry compatibility issues with PostHog
- Updated test assertions to properly include max_distance parameter

### Changed

- Refactored argument namespace creation into a shared function for better code organization
- Improved dependency management by consolidating dev dependencies into pyproject.toml
- Enhanced code documentation and logging clarity

## [3.0.0] - 2025-09-26

### Changed

- Overhauled plugin approach, plugins have easier access to core zk-chat services like llm, filesystem, memory
- Integrated rich throughout for nicer and more consistent command-line appearance

## [2.6.1] - 2025-04-05

### Added

- Added a friendlier banner for the CLI

## [2.6.0] - 2025-04-01

### Added

- Visual analysis capability for images in Zettelkasten
  - Added AnalyzeImage tool for examining and describing image content
  - Added support for configuring a separate visual model
  - Updated CLI and GUI to support visual model selection
- ResolveWikiLink tool for converting wikilinks to relative file paths for navigation between documents

### Changed

- Locked chromadb version to 0.6.3 and chroma-hnswlib to 0.7.6 for compatibility

## [2.5.1] - 2025-03-28

### Fixed

- Improved new (to zk-chat) vault and first-time installation experience

### Changed

- Updated README and refactored CLI and config for model handling and environment setup
- Streamlined vault path handling and gateway selection in CLI
- Refactored commit message generation to use updated LLM method

## [2.5.0] - 2025-03-26

### Added

- Document deletion functionality for better document management
  - Added DeleteZkDocument tool for safely removing documents from the Zettelkasten
  - Implemented safeguards to prevent accidental deletion of non-existent documents

## [2.4.0] - 2025-03-25

### Added

- Document renaming functionality
- List documents tool for better document management

### Changed

- Enhanced function descriptions for Zettelkasten tools to improve clarity and usability

## [2.3.0] - 2025-03-24

### Changed

- Added the ability to select (per vault) which gateway to use (Ollama or OpenAI) for chat
- Improved code organization and documentation
- Enhanced error handling and logging
- Performance optimizations

## [2.2.0] - 2025-03-23

### Added

- Git integration for vault management
  - Added GitGateway for Git operations
  - Added UncommittedChanges tool to view pending changes
  - Added CommitChanges tool with AI-generated commit messages
  - Added --git command-line flag to enable Git integration

## [2.1.0] - 2025-03-22

### Added

- Added significantly improved document search
- Added class docstring for Zettelkasten class

### Changed

- Updated requirements.txt to match dependencies in pyproject.toml
- Removed unnecessary f-string in logger.info call

## [2.0.0] - 2025-03-22

### Added

- Vault path argument for command-line tools
- Bookmark management for vault paths in CLI
- Global configuration handling
- MarkdownUtilities for handling markdown files with metadata
- MarkdownFilesystemGateway for markdown file operations

### Changed

- **Breaking**: Refactored ChromaGateway to support multiple collections
- **Breaking**: Updated Zettelkasten integration with new gateway architecture
- Streamlined bookmark handling in CLI by removing deprecated options

## [1.5.1] - 2025-03-09

### Fixed

- Properly passing LLM instance to plugins to enable LLM capabilities

## [1.5.0] - 2025-03-09

### Added

- **Breaking**: Enhanced plugin system to provide plugins with access to LLM capabilities
- Support for multiple indexers in Zettelkasten (one for excerpts and one for document titles/summaries)

### Changed

- Restructured Zettelkasten to externalize indexing functionality

## [1.4.0] - 2025-03-09

### Added

- Enhanced testing guidelines with detailed BDD-style section
- Configuration passing to plugin initialization

### Changed

- Renamed internal "chunks" concept to "excerpts" for better clarity
- Extracted filesystem operations into a dedicated filesystem gateway
- Improved code organization and structure

## [1.3.0] - 2025-03-03

### Added

- Plugin system for adding tools

### Changed

- Removed wikipedia lookup tool and [made it a plugin](https://pypi.org/project/zk-rag-wikipedia/) instead

## [1.2.0] - 2025-03-02

### Added

- Smart Memory mechanism for long-term context retention
- Wikipedia Lookup tool for external knowledge

### Changed

- Enhanced configuration options through both CLI and GUI
- Improved model selection interface

## [1.1.0] - 2025-02-19

### Added

- Configurable Zettelkasten folder, use of ~/.zk_rag for configuration
- Document manipulation tools for creating and updating Zettelkasten content

### Changed

- Improved document indexing system
- Enhanced RAG query capabilities

## [1.0.0] - 2024-02-13

### Added

- Initial release
- Rudimentary Command-line interface
- RAG (Retrieval-Augmented Generation) queries
- Interactive chat with Zettelkasten context
- Integration with Ollama for local LLM support
- Markdown document indexing
- Basic document search and retrieval
