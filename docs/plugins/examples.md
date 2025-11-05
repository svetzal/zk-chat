# Plugin Examples

Real-world examples of zk-chat plugins.

## Wikipedia Lookup Plugin

Retrieve content from Wikipedia and optionally create documents.

```python
from pathlib import Path
from typing import Optional
import wikipedia
from mojentic.llm.tools.llm_tool import LLMTool
from pydantic import BaseModel
from zk_chat.services import ServiceProvider


class WikipediaContentResult(BaseModel):
    title: str
    content: str
    url: Optional[str]


class LookUpTopicOnWikipedia(LLMTool):
    """Tool for retrieving content from Wikipedia."""

    def __init__(self, service_provider: ServiceProvider):
        super().__init__()
        self.service_provider = service_provider

    def run(self, topic: str) -> str:
        try:
            # Search for the page
            search_results = wikipedia.search(topic)
            if not search_results:
                return WikipediaContentResult(
                    title="No results",
                    content=f"No Wikipedia articles found for '{topic}'",
                    url=None
                ).model_dump()

            # Get the top result
            page_title = search_results[0]
            page = wikipedia.page(page_title, auto_suggest=False)

            return WikipediaContentResult(
                title=page.title,
                content=page.summary,
                url=page.url
            ).model_dump()

        except wikipedia.DisambiguationError as e:
            # Handle disambiguation pages
            try:
                page = wikipedia.page(e.options[0], auto_suggest=False)
                return WikipediaContentResult(
                    title=page.title,
                    content=page.summary,
                    url=page.url
                ).model_dump()
            except:
                return WikipediaContentResult(
                    title="Disambiguation Error",
                    content=f"Multiple matches for '{topic}'. Be more specific.",
                    url=None
                ).model_dump()
        except Exception as e:
            return WikipediaContentResult(
                title="Error",
                content=f"Error retrieving Wikipedia content: {str(e)}",
                url=None
            ).model_dump()

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "lookup_topic_on_wikipedia",
                "description": "Retrieves information about a topic from Wikipedia.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to learn about."
                        }
                    },
                    "required": ["topic"]
                }
            }
        }
```

**Usage:**
```
You: Look up Alan Turing on Wikipedia

AI: Using tool: lookup_topic_on_wikipedia
[Wikipedia summary about Alan Turing]

You: Create a document from that information

AI: Using tool: write_document
Created: @Alan Turing.md
```

## Image Generator Plugin

Generate images using Stable Diffusion.

```python
from pathlib import Path
from zk_chat.services import ZkChatPlugin, ServiceProvider
from stable_diffusion_gateway import StableDiffusionGateway


class GenerateImage(ZkChatPlugin):
    """Generate images from descriptions using Stable Diffusion."""

    def __init__(self, service_provider: ServiceProvider, 
                 gateway=None):
        super().__init__(service_provider)
        self.gateway = gateway or StableDiffusionGateway()

    def run(self, image_description: str, base_filename: str) -> str:
        """Generate an image and save it.
        
        Parameters
        ----------
        image_description : str
            Text description of the image
        base_filename : str
            Base name for output file (without extension)
            
        Returns
        -------
        str
            Confirmation message with embedding syntax
        """
        vault_path = self.vault_path
        if not vault_path:
            return "Error: Vault path not available"

        filename = Path(vault_path) / f"{base_filename}.png"
        image = self.gateway.generate_image(image_description)
        image.save(filename)

        return f"""
The image has been generated and saved at `{base_filename}.png`.
You can embed it in markdown using: `![image]({base_filename}.png)`
""".strip()

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "generate_image",
                "description": "Generates a PNG image from a description using Stable Diffusion 3.5.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_description": {
                            "type": "string",
                            "description": "Detailed description of the image to generate."
                        },
                        "base_filename": {
                            "type": "string",
                            "description": "Filename without PNG extension."
                        }
                    },
                    "required": ["image_description", "base_filename"]
                }
            }
        }
```

**Usage:**
```
You: Generate an image of a serene mountain landscape

AI: Using tool: generate_image
Generated: mountain-landscape.png

The image has been saved. Embed with:
![image](mountain-landscape.png)
```

## Multi-Service Analysis Plugin

Example using multiple services together.

```python
from zk_chat.services import ZkChatPlugin, ServiceProvider, ServiceType


class DocumentAnalyzer(ZkChatPlugin):
    """Analyze documents using multiple zk-chat services."""

    def __init__(self, service_provider: ServiceProvider):
        super().__init__(service_provider)

    def run(self, document_path: str, analysis_type: str) -> str:
        """Analyze a document comprehensively."""
        
        # Check service availability
        if not self.has_service(ServiceType.ZETTELKASTEN):
            return "Error: Zettelkasten service not available"

        # Read the document
        zk = self.zettelkasten
        if not zk.document_exists(document_path):
            return f"Document not found: {document_path}"

        document = zk.read_document(document_path)

        # Use LLM for analysis
        llm = self.llm_broker
        analysis_prompt = f"""
        Analyze this document for: {analysis_type}

        Document content:
        {document.content}

        Provide detailed analysis focusing on the requested aspect.
        """

        analysis_result = llm.send(analysis_prompt)

        # Store in smart memory
        if self.smart_memory:
            memory_entry = f"Analysis of {document_path} for {analysis_type}: {analysis_result}"
            self.smart_memory.store(memory_entry)

        # Find related documents
        related_docs = zk.find_documents_related_to(analysis_result)

        result = f"""
## Analysis Result

{analysis_result}

## Related Documents

Found {len(related_docs)} related documents:
{', '.join([doc.relative_path for doc in related_docs[:5]])}

Analysis stored in smart memory for future reference.
"""
        return result

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "analyze_document",
                "description": "Perform comprehensive analysis of a document.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_path": {
                            "type": "string",
                            "description": "Path to the document"
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis (e.g., 'themes', 'arguments')"
                        }
                    },
                    "required": ["document_path", "analysis_type"]
                }
            }
        }
```

## Simple Example Template

Minimal plugin template to get started:

```python
import structlog
from zk_chat.services import ZkChatPlugin, ServiceProvider

logger = structlog.get_logger()


class MySimplePlugin(ZkChatPlugin):
    """Template for a simple plugin."""

    def __init__(self, service_provider: ServiceProvider):
        super().__init__(service_provider)
        logger.info("Initialized MySimplePlugin")

    def run(self, input_text: str) -> str:
        """Process input and return result."""
        
        # Example: Use filesystem
        fs = self.filesystem_gateway
        if fs.path_exists("README.md"):
            content = fs.read_file("README.md")
            logger.info("Read README", length=len(content))
        
        # Example: Use LLM
        llm = self.llm_broker
        response = llm.send(f"Process this: {input_text}")
        
        return f"Processed: {response}"

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "my_simple_plugin",
                "description": "A simple example plugin.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input_text": {
                            "type": "string",
                            "description": "Text to process"
                        }
                    },
                    "required": ["input_text"]
                }
            }
        }
```

**pyproject.toml:**

```toml
[project]
name = "my-simple-plugin"
version = "1.0.0"
description = "A simple zk-chat plugin"
requires-python = ">=3.11"
dependencies = ["mojentic>=0.8.2"]

[build-system]
requires = ["setuptools>=61.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project.entry-points]
zk_rag_plugins = { my_plugin = "my_plugin:MySimplePlugin" }

[tool.setuptools]
py-modules = ["my_plugin"]
```

## Published Plugins

### zk-rag-wikipedia

Wikipedia lookup and document creation.

**Installation:**
```bash
pipx inject zk-chat zk-rag-wikipedia
```

**Repository:** [GitHub](https://github.com/svetzal/zk-rag-wikipedia)

### zk-rag-image-generator

Image generation with Stable Diffusion.

**Installation:**
```bash
pipx inject zk-chat zk-rag-image-generator
```

**Repository:** [GitHub](https://github.com/svetzal/zk-rag-image-generator)

## Development Tips

### Testing Plugins

```python
# Test your plugin locally
def test_plugin():
    from zk_chat.services import ServiceProvider, ServiceRegistry
    
    # Create mock services
    registry = ServiceRegistry()
    # Add services to registry...
    
    provider = ServiceProvider(registry)
    plugin = MyPlugin(provider)
    
    result = plugin.run("test input")
    print(result)
```

### Debugging

Use structured logging:

```python
logger.debug("Processing", input=input_data)
logger.info("Completed", result_length=len(result))
logger.error("Failed", error=str(e))
```

### Error Messages

Provide helpful error messages:

```python
if not document_path:
    return "Error: document_path is required. Provide the path to a document in your vault."

if not document_path.endswith('.md'):
    return "Error: Only markdown files (.md) are supported."
```

## See Also

- [Plugin Development Guide](guide.md) - Full development guide
- [Available Tools](../features/tools.md) - Built-in tools
- [MCP Servers](../features/mcp-servers.md) - Alternative extension method
