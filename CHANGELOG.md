# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Next]

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
