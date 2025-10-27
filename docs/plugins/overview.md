# Plugin Development Overview

Extend Zk-Chat with custom tools through its powerful plugin system.

## What Are Plugins?

Plugins are custom tools that extend Zk-Chat's capabilities. They:

- Inherit from the `LLMTool` base class
- Are automatically discovered and loaded
- Have access to the same runtime environment as built-in tools
- Can interact with your Zettelkasten, AI models, and more

## Why Create Plugins?

Create plugins to:

- Add domain-specific functionality
- Integrate external services or APIs
- Automate custom workflows
- Extend AI capabilities for your use case

## Example Plugins

### Available Plugins

- **[zk-rag-wikipedia](https://pypi.org/project/zk-rag-wikipedia/)**: Look up information on Wikipedia and create documents from results
- **[zk-rag-image-generator](https://pypi.org/project/zk-rag-image-generator/)**: Generate images using Stable Diffusion 3.5 Medium

### Installation

```bash
# With pipx
pipx inject zk-chat zk-rag-wikipedia
pipx inject zk-chat zk-rag-image-generator

# With pip
pip install zk-rag-wikipedia
pip install zk-rag-image-generator
```

## Plugin Capabilities

Plugins have access to:

### Core Services

- **Filesystem Gateway**: File operations in the vault
- **LLM Broker**: Make AI requests
- **Zettelkasten**: Document operations
- **Smart Memory**: Long-term context storage

### Database Services

- **ChromaDB Gateway**: Vector database access
- **Vector Database**: Semantic search capabilities

### Gateway Services

- **Model Gateway**: Ollama/OpenAI access
- **Tokenizer Gateway**: Token counting and management

### Optional Services

- **Git Gateway**: Version control (when `--git` is enabled)
- **Application Config**: Access to configuration

## Quick Start

1. **[Create a Plugin](creating-plugins.md)**: Learn the basics of plugin development
2. **[Service Provider](service-provider.md)**: Understand how to access Zk-Chat services
3. **[Examples](examples.md)**: See complete plugin examples

## Plugin Architecture

### Discovery and Loading

Plugins are discovered via Python entry points in the `zk_rag_plugins` group.

When Zk-Chat starts, it:

1. Scans for plugins in the `zk_rag_plugins` entry point group
2. Loads each plugin class
3. Instantiates plugins with a `ServiceProvider`
4. Registers them as available tools

### Service Provider Pattern

Plugins receive a `ServiceProvider` that gives access to all Zk-Chat services. This scalable pattern means:

- New services can be added without changing plugin constructors
- Plugins only request the services they need
- Service availability is checked at runtime

### Tool Interface

All plugins must implement the `LLMTool` interface:

- `run()`: Execute the tool's functionality
- `descriptor`: OpenAI function descriptor for the LLM

The convenient `ZkChatPlugin` base class provides common functionality.

## Plugins vs MCP Servers

| Feature | Zk-Chat Plugins | MCP Servers |
|---------|----------------|-------------|
| Integration | Deep (access to all services) | External (separate process) |
| Development | Python only | Any language |
| Distribution | PyPI packages | Standalone executables |
| Startup | Always loaded | Loaded on demand |
| Use Cases | Vault-specific tools | General-purpose tools |

### When to Use Each

**Use Plugins for:**

- Tools that need direct vault access
- Integration with Zk-Chat's vector database
- Python-based functionality
- Vault-specific workflows

**Use MCP Servers for:**

- General-purpose tools (not vault-specific)
- Tools in other languages
- External service integrations
- Tools shared across multiple applications

## Development Resources

- [Creating Plugins](creating-plugins.md) - Step-by-step guide
- [Service Provider API](service-provider.md) - Available services
- [Examples](examples.md) - Complete plugin examples
- [PLUGINS.md](https://github.com/svetzal/zk-chat/blob/main/PLUGINS.md) - Comprehensive developer guide

## Next Steps

Ready to create your first plugin? Start with the [Creating Plugins](creating-plugins.md) guide.
