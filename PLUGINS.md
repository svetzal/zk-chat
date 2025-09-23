# ZK-RAG Plugin Developer Guide

This guide walks you through developing plugins for zk-rag, the command-line chat tool for your Zettelkasten. Plugins allow you to extend the chat agent with custom tools that integrate seamlessly with your knowledge base and the zk-rag runtime environment.

## Table of Contents

- [Overview](#overview)
- [Plugin Architecture](#plugin-architecture)
- [Creating Your First Plugin](#creating-your-first-plugin)
- [Available Runtime Resources](#available-runtime-resources)
- [Plugin Development Best Practices](#plugin-development-best-practices)
- [Packaging and Distribution](#packaging-and-distribution)
- [ZK-RAG Plugins vs Model Context Protocol (MCP)](#zk-rag-plugins-vs-model-context-protocol-mcp)
- [Example Plugins](#example-plugins)

## Overview

ZK-RAG plugins are tools that extend the functionality of the chat agent. They inherit from the `LLMTool` base class and are automatically discovered and loaded when zk-rag starts. Plugins have access to the same runtime environment as built-in tools, including:

- Access to the user's Zettelkasten vault
- Integration with the vector database (ChromaDB)
- LLM broker for making AI requests
- Filesystem gateway for consistent file operations
- Smart memory system for long-term context retention

## Plugin Architecture

### Core Components

1. **Plugin Discovery**: Plugins are discovered via Python entry points in the `zk_rag_plugins` group
2. **Tool Interface**: All plugins must inherit from `mojentic.llm.tools.llm_tool.LLMTool`
3. **Runtime Integration**: Plugins receive access to the vault path and LLM broker during initialization
4. **Automatic Loading**: The `_add_available_plugins()` function automatically loads and instantiates all discovered plugins

### Plugin Loading Mechanism

```python
def _add_available_plugins(tools, config: Config, llm: LLMBroker):
    eps = entry_points()
    plugin_entr_points = eps.select(group="zk_rag_plugins")
    for ep in plugin_entr_points:
        logging.info(f"Adding Plugin {ep.name}")
        plugin_class = ep.load()
        tools.append(plugin_class(vault=config.vault, llm=llm))
```

All plugins are instantiated with:
- `vault`: The absolute path to the user's Zettelkasten vault
- `llm`: An `LLMBroker` instance for making LLM requests

## Creating Your First Plugin

### Step 1: Set Up Your Plugin Package

Create a new Python package for your plugin:

```bash
mkdir my-zk-plugin
cd my-zk-plugin
```

### Step 2: Create the Plugin Class

Create your main plugin file (e.g., `my_plugin.py`):

```python
"""
Simple example plugin for zk-rag demonstrating the basic plugin interface.
This can be used as a template for creating your own plugins.
"""
import structlog
from mojentic.llm import LLMBroker
from mojentic.llm.tools.llm_tool import LLMTool

logger = structlog.get_logger()


class MyCustomTool(LLMTool):
    """A custom tool for zk-rag that demonstrates the plugin interface."""
    
    def __init__(self, vault: str, llm: LLMBroker):
        """Initialize the plugin with vault path and LLM broker.
        
        Args:
            vault: Absolute path to the user's Zettelkasten vault
            llm: LLMBroker instance for making LLM requests
        """
        super().__init__()
        self.vault = vault
        self.llm = llm
        logger.info("Initialized MyCustomTool plugin", vault=vault)
    
    def run(self, user_input: str) -> str:
        """Execute the plugin's main functionality.
        
        Args:
            user_input: Input from the user
            
        Returns:
            str: Result to be returned to the chat
        """
        logger.info("Running MyCustomTool", user_input=user_input)
        
        # Your plugin logic here
        result = f"Processed: {user_input} in vault: {self.vault}"
        
        return result
    
    @property
    def descriptor(self) -> dict:
        """Return the OpenAI function descriptor for this tool.
        
        This descriptor tells the LLM how to use your tool, including:
        - Function name and description
        - Parameters and their types
        - Required parameters
        """
        return {
            "type": "function",
            "function": {
                "name": "my_custom_tool",
                "description": "A demonstration tool that processes user input with access to the vault",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_input": {
                            "type": "string",
                            "description": "The input text to process"
                        }
                    },
                    "required": ["user_input"]
                }
            }
        }
```

### Step 3: Configure Entry Points

Create a `pyproject.toml` file to register your plugin:

```toml
[project]
name = "my-zk-plugin"
version = "1.0.0"
description = "My custom ZK-RAG plugin"
requires-python = ">=3.11"
dependencies = [
    "mojentic>=0.6.1",
]

[build-system]
requires = ["setuptools>=61.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project.entry-points]
zk_rag_plugins = { my_plugin = "my_plugin:MyCustomTool" }

[tool.setuptools]
py-modules = ["my_plugin"]
```

### Step 4: Install and Test

Install your plugin in development mode:

```bash
pip install -e .
```

Now your plugin will be automatically loaded when you run zk-rag!

## Available Runtime Resources

Plugins have access to the full zk-rag runtime environment. Here are the key resources you can leverage:

### 1. Vault Access
- **Purpose**: Direct filesystem access to the user's Zettelkasten
- **Usage**: Read, create, and modify documents in the vault
- **Access**: Via the `vault` parameter (absolute path)

```python
from pathlib import Path

def read_vault_file(self, relative_path: str) -> str:
    """Read a file from the vault."""
    file_path = Path(self.vault) / relative_path
    return file_path.read_text()
```

### 2. LLM Broker
- **Purpose**: Make requests to the configured LLM
- **Usage**: Generate text, analyze content, create summaries
- **Access**: Via the `llm` parameter

```python
def analyze_text(self, text: str) -> str:
    """Use the LLM to analyze text."""
    prompt = f"Analyze this text and provide insights: {text}"
    return self.llm.send(prompt)
```

### 3. Filesystem Gateway (Advanced)
- **Purpose**: Consistent filesystem operations with the zk-rag system
- **Usage**: For advanced file operations that need to integrate with zk-rag's filesystem abstraction
- **Access**: You can instantiate `MarkdownFilesystemGateway` if needed

```python
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway

def __init__(self, vault: str, llm: LLMBroker):
    super().__init__()
    self.vault = vault
    self.llm = llm
    self.filesystem_gateway = MarkdownFilesystemGateway(vault)
```

### 4. Logging
- **Purpose**: Consistent logging with the zk-rag system
- **Usage**: Use `structlog` for all logging operations
- **Access**: Import and use `structlog.get_logger()`

```python
import structlog

logger = structlog.get_logger()

def run(self, input_data: str) -> str:
    logger.info("Processing input", input_length=len(input_data))
    # ... plugin logic ...
    logger.info("Processing complete", result_length=len(result))
    return result
```

## Plugin Development Best Practices

### 1. Error Handling
Always handle errors gracefully and return meaningful error messages:

```python
def run(self, input_data: str) -> str:
    try:
        # Plugin logic here
        return result
    except Exception as e:
        logger.error("Plugin error", error=str(e))
        return f"Error in plugin: {str(e)}"
```

### 2. Input Validation
Validate inputs and provide clear feedback:

```python
def run(self, file_path: str) -> str:
    if not file_path:
        return "Error: file_path parameter is required"
    
    if not file_path.endswith('.md'):
        return "Error: Only markdown files are supported"
    
    # Continue with plugin logic...
```

### 3. Descriptive Function Descriptors
Make your tool easy for the LLM to understand and use:

```python
@property
def descriptor(self) -> dict:
    return {
        "type": "function",
        "function": {
            "name": "generate_summary",
            "description": "Generate a concise summary of a document from the Zettelkasten. Use this when the user asks for a summary of a specific document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_path": {
                        "type": "string",
                        "description": "The relative path to the document within the Zettelkasten (e.g., 'notes/research.md')"
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Maximum length of the summary in words (default: 100)",
                        "default": 100
                    }
                },
                "required": ["document_path"]
            }
        }
    }
```

### 4. Use Structured Logging
Include relevant context in your log messages:

```python
logger.info(
    "Generated summary",
    document_path=document_path,
    original_length=len(content),
    summary_length=len(summary)
)
```

## Packaging and Distribution

### 1. Package Structure
```
my-zk-plugin/
├── my_plugin.py
├── pyproject.toml
├── README.md
└── requirements.txt (optional)
```

### 2. Publishing to PyPI
```bash
pip install build twine
python -m build
twine upload dist/*
```

### 3. Installation by Users
Users can install your plugin with:

```bash
# Using pipx (recommended)
pipx inject zk-rag my-zk-plugin

# Using pip in a virtual environment
pip install my-zk-plugin
```

## ZK-RAG Plugins vs Model Context Protocol (MCP)

### ZK-RAG Plugins Advantages

**🔧 Deep Runtime Integration**
- Direct access to the user's Zettelkasten vault
- Integration with zk-rag's vector database and Smart Memory
- Access to the same LLM broker used by the system
- Consistent filesystem operations via the filesystem gateway

**📊 Shared Context**
- Plugins operate within the same chat session context
- Access to conversation history and system state
- Seamless integration with other tools and plugins

**🚀 Performance Benefits**
- No inter-process communication overhead
- Direct memory access to shared resources
- Faster execution for file operations and database queries

**🛠️ Developer Experience**
- Simple Python class inheritance model
- Automatic discovery and loading
- Rich runtime environment with logging, error handling, and utilities

### MCP Advantages

**🔒 Isolation**
- Complete separation from the host application
- Independent deployment and updates
- Better security boundaries

**🌐 Language Agnostic**
- Can be implemented in any programming language
- Standardized protocol across different AI systems
- Greater portability between different chat systems

**⚡ Independent Operation**
- Plugins can run on separate machines
- Scalable architecture for resource-intensive operations
- Independent failure domains

### When to Choose ZK-RAG Plugins

Choose zk-rag plugins when you need:

- **Deep integration** with the Zettelkasten and its metadata
- **Access to the vector database** for semantic search capabilities
- **Consistent file operations** that align with zk-rag's document handling
- **Shared context** with other tools in the chat session
- **Simple development** with Python and familiar object-oriented patterns
- **Performance-critical operations** that benefit from direct memory access
- **Access to Smart Memory** for long-term context retention across sessions

### When to Choose MCP

Choose MCP when you need:

- **Language flexibility** (non-Python implementations)
- **Strong isolation** from the host system
- **Independent deployment** and scaling
- **Cross-platform compatibility** with multiple AI systems
- **Resource-intensive operations** that benefit from separate processes

### MCP Integration in ZK-RAG

Note that zk-rag also includes built-in MCP server functionality (`zk_chat/mcp.py`) that exposes specific zk-rag tools via the Model Context Protocol. This allows external MCP clients to access zk-rag's document and memory capabilities independently. However, this is primarily intended for integration with other AI systems rather than extending zk-rag's own functionality.

## Example Plugins

### 1. Wikipedia Lookup Plugin

The [zk-rag-wikipedia](https://github.com/svetzal/zk-rag-wikipedia) plugin demonstrates:
- External API integration
- Structured data return (Pydantic models)
- Error handling for disambiguation and API failures

```python
class LookUpTopicOnWikipedia(LLMTool):
    def __init__(self, vault: str, llm: LLMBroker):
        super().__init__()
        self.vault = vault

    def run(self, topic: str) -> str:
        try:
            search_results = wikipedia.search(topic)
            if not search_results:
                return WikipediaContentResult(
                    title="No results",
                    content=f"No Wikipedia articles found for '{topic}'",
                    url=None
                ).model_dump()

            page_title = search_results[0]
            page = wikipedia.page(page_title, auto_suggest=False)

            return WikipediaContentResult(
                title=page.title,
                content=page.summary,
                url=page.url
            ).model_dump()
        except Exception as e:
            return WikipediaContentResult(
                title="Error",
                content=f"An error occurred: {str(e)}",
                url=None
            ).model_dump()
```

### 2. Image Generator Plugin

The [zk-rag-image-generator](https://github.com/svetzal/zk-rag-image-generator) plugin demonstrates:
- File creation in the vault
- Integration with external ML models
- Returning markdown-compatible references

```python
class GenerateImage(LLMTool):
    def __init__(self, vault: str, llm: LLMBroker, gateway: Optional[StableDiffusionGateway] = None):
        super().__init__()
        self.vault = vault
        self.gateway = gateway or StableDiffusionGateway()

    def run(self, image_description: str, base_filename: str) -> str:
        filename = Path(self.vault) / f"{base_filename}.png"
        image = self.gateway.generate_image(image_description)
        image.save(filename)
        return f"Image saved at `{base_filename}.png`. Embed with: `![image]({base_filename}.png)`"
```

## Getting Help

- **Issues**: Report bugs or feature requests on the [zk-rag GitHub repository](https://github.com/svetzal/zk-rag/issues)
- **Discussions**: Ask questions in the [GitHub Discussions](https://github.com/svetzal/zk-rag/discussions)
- **Example Code**: Check out the existing plugin repositories for inspiration

Happy plugin development! 🚀