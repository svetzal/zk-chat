# Plugin Development Guide

Extend zk-chat with custom tools through the plugin system.

## Overview

Zk-chat plugins are Python packages that add new capabilities to the AI assistant. Plugins have access to:

- Your Zettelkasten vault
- Vector database (ChromaDB)
- LLM broker
- Filesystem gateway  
- Smart memory
- And more...

## Quick Start

### 1. Create Plugin Package

```bash
mkdir my-zk-plugin
cd my-zk-plugin
```

### 2. Create Plugin Class

Create `my_plugin.py`:

```python
import structlog
from zk_chat.services import ZkChatPlugin, ServiceProvider

logger = structlog.get_logger()


class MyCustomTool(ZkChatPlugin):
    """A custom tool for zk-chat."""

    def __init__(self, service_provider: ServiceProvider):
        super().__init__(service_provider)
        logger.info("Initialized MyCustomTool")

    def run(self, user_input: str) -> str:
        """Execute the plugin's functionality."""
        # Access services
        vault_path = self.vault_path
        filesystem = self.filesystem_gateway
        llm = self.llm_broker
        
        # Your logic here
        result = f"Processed: {user_input}"
        return result

    @property
    def descriptor(self) -> dict:
        """Tell the LLM how to use this tool."""
        return {
            "type": "function",
            "function": {
                "name": "my_custom_tool",
                "description": "Processes user input",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_input": {
                            "type": "string",
                            "description": "Input to process"
                        }
                    },
                    "required": ["user_input"]
                }
            }
        }
```

### 3. Configure Entry Point

Create `pyproject.toml`:

```toml
[project]
name = "my-zk-plugin"
version = "1.0.0"
description = "My custom zk-chat plugin"
requires-python = ">=3.11"
dependencies = [
    "mojentic>=0.8.2",
]

[build-system]
requires = ["setuptools>=61.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project.entry-points]
zk_rag_plugins = { my_plugin = "my_plugin:MyCustomTool" }

[tool.setuptools]
py-modules = ["my_plugin"]
```

### 4. Install and Use

```bash
# Install in development mode
pip install -e .

# Or with pipx
pipx inject zk-chat .

# Plugin loads automatically
zk-chat interactive
```

## Available Services

Plugins can access these services through the `ServiceProvider`:

### Filesystem Gateway

Read/write files in the vault:

```python
def process_file(self, path: str) -> str:
    fs = self.filesystem_gateway
    if fs.path_exists(path):
        content = fs.read_file(path)
        # Process content...
        fs.write_file(path, modified_content)
        return "File processed"
    return "File not found"
```

### LLM Broker

Make AI requests:

```python
def analyze_with_ai(self, text: str) -> str:
    llm = self.llm_broker
    prompt = f"Analyze: {text}"
    return llm.send(prompt)
```

### Zettelkasten Service

Document operations and search:

```python
def find_related(self, query: str) -> str:
    zk = self.zettelkasten
    docs = zk.find_documents_related_to(query)
    return f"Found {len(docs)} documents"
```

### Smart Memory

Long-term context storage:

```python
def remember(self, info: str) -> str:
    memory = self.smart_memory
    memory.store(info)
    return "Stored in memory"
```

### Other Services

- **ChromaDB Gateway** - Vector database operations
- **Model Gateway** - Direct LLM access
- **Config** - Application configuration
- **Git Gateway** - Git operations (when enabled)

## Best Practices

### Error Handling

Always handle errors gracefully:

```python
def run(self, input_data: str) -> str:
    try:
        # Plugin logic
        return result
    except Exception as e:
        logger.error("Plugin error", error=str(e))
        return f"Error: {str(e)}"
```

### Input Validation

Validate inputs early:

```python
def run(self, file_path: str) -> str:
    if not file_path:
        return "Error: file_path required"
    
    if not file_path.endswith('.md'):
        return "Error: Only markdown files supported"
    
    # Continue...
```

### Descriptive Tool Descriptors

Help the LLM understand your tool:

```python
@property
def descriptor(self) -> dict:
    return {
        "type": "function",
        "function": {
            "name": "generate_summary",
            "description": "Generate a concise summary of a document. Use when user asks for a summary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_path": {
                        "type": "string",
                        "description": "Path to document (e.g., 'notes/research.md')"
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Max summary length in words (default: 100)",
                        "default": 100
                    }
                },
                "required": ["document_path"]
            }
        }
    }
```

### Logging

Use structured logging:

```python
logger.info(
    "Generated summary",
    document=doc_path,
    length=len(summary)
)
```

## Publishing

### Package Structure

```
my-zk-plugin/
├── my_plugin.py
├── pyproject.toml
├── README.md
└── requirements.txt (optional)
```

### Build and Publish

```bash
# Build
pip install build
python -m build

# Publish to PyPI
pip install twine
twine upload dist/*
```

### Installation by Users

Users install with:

```bash
# With pipx (recommended)
pipx inject zk-chat my-zk-plugin

# With pip
pip install my-zk-plugin
```

## Plugin vs MCP

**Choose zk-chat plugins when:**
- Need vault/database access
- Want deep integration
- Using Python
- Need best performance

**Choose MCP when:**
- Using non-Python language
- Need process isolation
- Want cross-system compatibility
- Have resource-intensive operations

See [MCP Servers](../features/mcp-servers.md) for MCP details.

## Advanced Topics

### Service Availability

Check if services are available:

```python
from zk_chat.services import ServiceType

def check_git(self):
    provider = self.service_provider
    if provider.has_service(ServiceType.GIT_GATEWAY):
        git = provider.get_git_gateway()
        # Use git...
```

### Direct LLMTool Inheritance

For more control, inherit from `LLMTool` directly:

```python
from mojentic.llm.tools.llm_tool import LLMTool
from zk_chat.services import ServiceProvider

class MyTool(LLMTool):
    def __init__(self, service_provider: ServiceProvider):
        super().__init__()
        self.provider = service_provider
        
    def run(self, input: str) -> str:
        # Access services manually
        fs = self.provider.get_filesystem_gateway()
        return "Result"
```

## Example Use Cases

### Content Analyzer

Analyze documents for specific patterns:

```python
class ContentAnalyzer(ZkChatPlugin):
    def run(self, document_path: str) -> str:
        zk = self.zettelkasten
        doc = zk.read_document(document_path)
        
        llm = self.llm_broker
        analysis = llm.send(f"Analyze: {doc.content}")
        
        self.smart_memory.store(f"Analysis of {document_path}: {analysis}")
        return analysis
```

### Link Analyzer

Find broken links:

```python
class LinkChecker(ZkChatPlugin):
    def run(self) -> str:
        fs = self.filesystem_gateway
        broken = []
        
        for doc in fs.list_markdown_files():
            # Check wikilinks...
            pass
            
        return f"Found {len(broken)} broken links"
```

### External Data Importer

Import data from external sources:

```python
class DataImporter(ZkChatPlugin):
    def run(self, source: str) -> str:
        # Fetch external data
        data = fetch_from_api(source)
        
        # Create document
        fs = self.filesystem_gateway
        fs.write_file(f"import-{source}.md", data)
        
        return f"Imported from {source}"
```

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/svetzal/zk-chat/issues)
- **Discussions**: [GitHub Discussions](https://github.com/svetzal/zk-chat/discussions)
- **Examples**: See [Plugin Examples](examples.md)
- **PLUGINS.md**: Full developer guide in repository

## See Also

- [Plugin Examples](examples.md) - Real plugin implementations
- [Available Tools](../features/tools.md) - Built-in tools
- [MCP Servers](../features/mcp-servers.md) - Alternative extension method
