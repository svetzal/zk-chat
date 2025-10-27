# Creating Plugins

Learn how to create your first Zk-Chat plugin.

## Prerequisites

- Python 3.11 or later
- Basic understanding of Python classes and packages
- Familiarity with Zk-Chat usage

## Quick Start

### 1. Create Package Structure

```bash
mkdir my-zk-plugin
cd my-zk-plugin
```

Create the following structure:

```
my-zk-plugin/
├── my_plugin/
│   ├── __init__.py
│   └── tool.py
├── pyproject.toml
└── README.md
```

### 2. Create the Plugin Class

`my_plugin/tool.py`:

```python
"""My custom Zk-Chat plugin."""
import structlog
from zk_chat.services import ZkChatPlugin, ServiceProvider

logger = structlog.get_logger()


class MyCustomTool(ZkChatPlugin):
    """A custom tool for zk-chat."""

    def __init__(self, service_provider: ServiceProvider):
        super().__init__(service_provider)
        logger.info("Initialized MyCustomTool plugin")

    def run(self, query: str) -> str:
        """Execute the plugin's main functionality.
        
        Args:
            query: User input
            
        Returns:
            Result to be returned to the chat
        """
        logger.info("Running MyCustomTool", query=query)
        
        # Access services
        vault_path = self.vault_path
        filesystem = self.filesystem_gateway
        
        # Your plugin logic here
        result = f"Processed: {query} in vault: {vault_path}"
        
        return result

    @property
    def descriptor(self) -> dict:
        """Return the OpenAI function descriptor for this tool."""
        return {
            "type": "function",
            "function": {
                "name": "my_custom_tool",
                "description": "Description of what your tool does",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The query to process"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
```

### 3. Configure Package

`pyproject.toml`:

```toml
[project]
name = "my-zk-plugin"
version = "0.1.0"
description = "My custom Zk-Chat plugin"
requires-python = ">=3.11"
dependencies = [
    "zk-chat>=3.0.0",
]

[project.entry-points.zk_rag_plugins]
my_custom_tool = "my_plugin.tool:MyCustomTool"

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
```

### 4. Test Locally

```bash
# Install in development mode
pip install -e .

# Test with Zk-Chat
zk-chat interactive --vault /path/to/vault
```

Your plugin will be automatically loaded and available to the AI.

### 5. Package and Distribute

```bash
# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## Plugin Development Tips

1. **Use the ZkChatPlugin Base Class**: Provides convenient access to services
2. **Log Important Events**: Use structlog for debugging
3. **Handle Errors Gracefully**: Return helpful error messages
4. **Test Thoroughly**: Test with different inputs and scenarios
5. **Document Well**: Clear docstrings and README

## Next Steps

- [Service Provider API](service-provider.md) - Learn about available services
- [Examples](examples.md) - See complete plugin examples
- [Full Developer Guide](https://github.com/svetzal/zk-chat/blob/main/PLUGINS.md) - Comprehensive documentation
