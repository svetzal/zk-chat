# Service Provider API

Learn how to access Zk-Chat services in your plugins through the Service Provider.

## Overview

The `ServiceProvider` gives plugins access to all Zk-Chat services. This scalable pattern allows new services to be added without changing plugin code.

## Accessing Services

### Using ZkChatPlugin Base Class

The easiest way is to inherit from `ZkChatPlugin`:

```python
from zk_chat.services import ZkChatPlugin, ServiceProvider

class MyPlugin(ZkChatPlugin):
    def __init__(self, service_provider: ServiceProvider):
        super().__init__(service_provider)
        
    def run(self, input: str) -> str:
        # Convenient property access
        vault_path = self.vault_path
        fs = self.filesystem_gateway
        llm = self.llm_broker
        zk = self.zettelkasten
        memory = self.smart_memory
        
        # Your plugin logic
        return "result"
```

### Direct Service Access

Or access services directly:

```python
from zk_chat.services import ServiceProvider

def __init__(self, service_provider: ServiceProvider):
    self.service_provider = service_provider
    
def run(self, input: str) -> str:
    fs = self.service_provider.get_filesystem_gateway()
    llm = self.service_provider.get_llm_broker()
    # etc.
```

## Available Services

### Core Services

#### Filesystem Gateway

Access file operations in the vault:

```python
fs = self.filesystem_gateway

# Check if file exists
if fs.path_exists("document.md"):
    # Read file
    content = fs.read_file("document.md")
    
    # Write file
    fs.write_file("new-doc.md", "content")
    
    # List files
    files = fs.list_markdown_files()
```

#### LLM Broker

Make AI requests:

```python
llm = self.llm_broker

from mojentic.llm.gateways.models import LLMMessage

messages = [LLMMessage(content="Your prompt")]
response = llm.generate(messages)
```

#### Zettelkasten

Document operations:

```python
zk = self.zettelkasten

# Find documents
docs = zk.find_documents("query")

# Read document
content = zk.read_document("document-name")

# List all documents
all_docs = zk.list_documents()
```

#### Smart Memory

Long-term context storage:

```python
memory = self.smart_memory

# Store information
memory.store("Important fact about user preferences")

# Retrieve information
results = memory.retrieve("user preferences")
```

### Database Services

#### Chroma Gateway

Vector database access:

```python
chroma = self.service_provider.get_chroma_gateway()

# Query the vector database
results = chroma.query(
    query_text="search query",
    n_results=10
)
```

### Configuration

#### Vault Path

Get the vault path:

```python
vault_path = self.vault_path
```

#### Application Config

Access configuration:

```python
config = self.service_provider.get_config()
model = config.model
gateway = config.gateway
```

### Optional Services

#### Git Gateway

When Git is enabled (`--git` flag):

```python
git = self.service_provider.get_git_gateway()

if git:
    # View uncommitted changes
    diff = git.get_uncommitted_changes()
    
    # Commit changes
    git.commit_changes("Commit message")
```

## Service Availability

Not all services are always available. Check before using:

```python
git = self.service_provider.get_git_gateway()
if git:
    # Git is enabled
    git.commit_changes("message")
else:
    # Git is not enabled
    return "Git integration not enabled"
```

## Complete Example

```python
from zk_chat.services import ZkChatPlugin, ServiceProvider
import structlog

logger = structlog.get_logger()


class DocumentAnalyzer(ZkChatPlugin):
    """Analyzes document statistics."""
    
    def __init__(self, service_provider: ServiceProvider):
        super().__init__(service_provider)
        
    def run(self, pattern: str) -> str:
        """Analyze documents matching pattern."""
        
        # Use filesystem to list documents
        fs = self.filesystem_gateway
        docs = [f for f in fs.list_markdown_files() 
                if pattern in f]
        
        # Use zettelkasten to read them
        zk = self.zettelkasten
        total_words = 0
        
        for doc in docs:
            content = zk.read_document(doc)
            total_words += len(content.split())
        
        # Store result in smart memory
        memory = self.smart_memory
        memory.store(
            f"Document analysis: {len(docs)} documents "
            f"matching '{pattern}' contain {total_words} words"
        )
        
        return f"Analyzed {len(docs)} documents: {total_words} total words"
    
    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "analyze_documents",
                "description": "Analyze documents matching a pattern",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Pattern to match in filenames"
                        }
                    },
                    "required": ["pattern"]
                }
            }
        }
```

## Best Practices

1. **Check Service Availability**: Not all services are always present
2. **Use ZkChatPlugin Base Class**: Provides convenient property access
3. **Handle Errors**: Services may fail; handle exceptions gracefully
4. **Log Service Usage**: Use structlog to log service interactions
5. **Respect Vault Boundaries**: Only access files within the vault

## Next Steps

- [Examples](examples.md) - See complete plugin examples
- [Creating Plugins](creating-plugins.md) - Build your first plugin
- [Full API Reference](https://github.com/svetzal/zk-chat/blob/main/PLUGINS.md) - Comprehensive documentation
