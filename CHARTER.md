# Project Charter

## Purpose

zk-chat is a RAG-based CLI and GUI tool that lets users have AI-powered conversations with their Zettelkasten (markdown knowledge base). It indexes notes into a vector database, retrieves relevant content via semantic search, and uses an LLM to generate grounded answers — running locally with Ollama or via OpenAI.

## Goals

- Provide accurate, context-grounded answers by retrieving relevant notes before generating responses
- Support fully local operation (Ollama + ChromaDB) so no data leaves the user's machine
- Traverse the knowledge graph through wikilinks, backlinks, and forward links to surface connections
- Offer an extensible plugin and MCP tool system for integrating external capabilities
- Optionally allow AI-assisted content creation with git-tracked safety controls
- Work seamlessly with Obsidian, Logseq, and other markdown-based note systems

## Non-Goals

- Replacing or reimplementing a note-taking application — zk-chat reads and queries an existing vault
- Hosting or managing LLM infrastructure — it delegates to Ollama or OpenAI
- Supporting non-markdown document formats (PDF, DOCX, etc.)
- Providing a collaborative or multi-user environment

## Target Users

Individual knowledge workers who maintain a markdown Zettelkasten and want to query, explore, and optionally extend their notes through conversational AI — particularly those who value local-first, privacy-respecting tooling.
