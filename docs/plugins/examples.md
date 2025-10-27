# Plugin Examples

Complete examples of Zk-Chat plugins.

## Simple Query Plugin

A basic plugin that demonstrates core concepts:

```python
"""Simple query plugin for zk-chat."""
import structlog
from zk_chat.services import ZkChatPlugin, ServiceProvider

logger = structlog.get_logger()


class SimpleQueryTool(ZkChatPlugin):
    """Performs simple queries on the vault."""

    def __init__(self, service_provider: ServiceProvider):
        super().__init__(service_provider)
        logger.info("Initialized SimpleQueryTool")

    def run(self, search_term: str) -> str:
        """Search for a term in document titles.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching documents
        """
        fs = self.filesystem_gateway
        
        # Find matching files
        matching_files = [
            f for f in fs.list_markdown_files()
            if search_term.lower() in f.lower()
        ]
        
        if not matching_files:
            return f"No documents found matching '{search_term}'"
        
        return f"Found {len(matching_files)} documents:\n" + "\n".join(
            f"- {f}" for f in matching_files
        )

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "search_document_titles",
                "description": "Search for documents by title",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_term": {
                            "type": "string",
                            "description": "Term to search for in titles"
                        }
                    },
                    "required": ["search_term"]
                }
            }
        }
```

## Document Statistics Plugin

A more complex plugin using multiple services:

```python
"""Document statistics plugin for zk-chat."""
import structlog
from zk_chat.services import ZkChatPlugin, ServiceProvider
from datetime import datetime

logger = structlog.get_logger()


class DocumentStatsTools(ZkChatPlugin):
    """Provides document statistics and analysis."""

    def __init__(self, service_provider: ServiceProvider):
        super().__init__(service_provider)
        logger.info("Initialized DocumentStatsTools")

    def run(self, stat_type: str = "summary") -> str:
        """Get document statistics.
        
        Args:
            stat_type: Type of statistics (summary, detailed, recent)
            
        Returns:
            Statistics report
        """
        fs = self.filesystem_gateway
        zk = self.zettelkasten
        
        docs = list(fs.list_markdown_files())
        total_docs = len(docs)
        
        if stat_type == "summary":
            total_words = 0
            for doc in docs:
                try:
                    content = zk.read_document(doc)
                    total_words += len(content.split())
                except Exception as e:
                    logger.warning(f"Error reading {doc}: {e}")
            
            avg_words = total_words / total_docs if total_docs > 0 else 0
            
            return (
                f"Vault Statistics:\n"
                f"- Total documents: {total_docs}\n"
                f"- Total words: {total_words:,}\n"
                f"- Average words per document: {avg_words:.0f}"
            )
        
        elif stat_type == "recent":
            # Get recently modified files
            recent_docs = []
            for doc in docs:
                path = fs.join_path(doc)
                if fs.path_exists(path):
                    mtime = fs.get_modified_time(path)
                    recent_docs.append((doc, mtime))
            
            recent_docs.sort(key=lambda x: x[1], reverse=True)
            top_10 = recent_docs[:10]
            
            result = "Recently Modified Documents:\n"
            for doc, mtime in top_10:
                date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                result += f"- {doc} ({date})\n"
            
            return result
        
        else:
            return f"Unknown stat type: {stat_type}"

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "get_document_stats",
                "description": "Get statistics about documents in the vault",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stat_type": {
                            "type": "string",
                            "enum": ["summary", "recent"],
                            "description": "Type of statistics to retrieve"
                        }
                    }
                }
            }
        }
```

## External API Integration Plugin

Example of integrating an external service:

```python
"""Weather plugin for zk-chat (example)."""
import structlog
import requests
from zk_chat.services import ZkChatPlugin, ServiceProvider

logger = structlog.get_logger()


class WeatherTool(ZkChatPlugin):
    """Get weather information and optionally save to vault."""

    def __init__(self, service_provider: ServiceProvider):
        super().__init__(service_provider)
        logger.info("Initialized WeatherTool")

    def run(self, location: str, save_to_vault: bool = False) -> str:
        """Get weather for a location.
        
        Args:
            location: City name or location
            save_to_vault: Whether to save result to vault
            
        Returns:
            Weather information
        """
        # Make API call (example - replace with real API)
        try:
            # This is a placeholder - use a real weather API
            weather_data = f"Weather for {location}: Sunny, 72°F"
            
            if save_to_vault:
                fs = self.filesystem_gateway
                filename = f"weather-{location.replace(' ', '-').lower()}.md"
                content = f"# Weather for {location}\n\n{weather_data}\n"
                
                fs.write_file(filename, content)
                logger.info(f"Saved weather to {filename}")
                
                return f"{weather_data}\n\nSaved to {filename}"
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return f"Error: {str(e)}"

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City or location name"
                        },
                        "save_to_vault": {
                            "type": "boolean",
                            "description": "Save result to vault"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
```

## Real-World Examples

### Wikipedia Plugin

See [zk-rag-wikipedia](https://github.com/svetzal/zk-rag-wikipedia) for a complete example that:

- Queries Wikipedia API
- Formats results as markdown
- Creates documents in the vault

### Image Generator Plugin

See [zk-rag-image-generator](https://github.com/svetzal/zk-rag-image-generator) for an example that:

- Integrates with Stable Diffusion API
- Generates images based on prompts
- Saves images to the vault

## Best Practices Demonstrated

1. **Error Handling**: All examples include try/except blocks
2. **Logging**: Using structlog for debugging
3. **Service Usage**: Accessing services through the provider
4. **Descriptors**: Complete function descriptors for the LLM
5. **Documentation**: Docstrings for all methods

## Next Steps

- [Creating Plugins](creating-plugins.md) - Build your own plugin
- [Service Provider](service-provider.md) - Learn about available services
- [Full Developer Guide](https://github.com/svetzal/zk-chat/blob/main/PLUGINS.md) - Comprehensive documentation
