# Visual Analysis

Zk-Chat can analyze images in your Zettelkasten using multimodal AI models.

## Setup

To use visual analysis, you need to configure a visual model:

### With Ollama

```bash
# Pull a visual model
ollama pull llava

# Use it in Zk-Chat
zk-chat interactive --visual-model llava
```

Other Ollama visual models:

- `llava` - General purpose vision model
- `bakllava` - Alternative vision model

### With OpenAI

```bash
export OPENAI_API_KEY=your_api_key_here
zk-chat interactive --gateway openai --visual-model gpt-4-vision
```

## Using Visual Analysis

Once configured, you can ask the AI about images:

```
You: What's in the image at diagrams/architecture.png?
```

```
You: Can you describe the chart in assets/sales-data.jpg?
```

```
You: Analyze the photo in attachments/meeting-whiteboard.png
```

The AI will:

1. Locate the image in your vault
2. Analyze it using the visual model
3. Describe the content
4. Answer your questions about it

## Use Cases

### Documentation

- Understanding diagrams in your notes
- Extracting information from charts and graphs
- Analyzing screenshots

### Research

- Analyzing research images
- Extracting data from visual sources
- Comparing images

### Knowledge Management

- Getting descriptions of visual content
- Extracting text from images (OCR-like)
- Cataloging image content

## Example Workflow

```
You: What's in the image at diagrams/system-architecture.png?
AI: The image shows a system architecture diagram with three main components: 
    a web server, an application server, and a database. They are connected 
    with arrows showing data flow...

You: What database is shown?
AI: Based on the diagram, it appears to be PostgreSQL.

You: Create a document summarizing this architecture
AI: [Creates a document with the architecture details extracted from the image]
```

## Limitations

- Accuracy depends on the visual model used
- Some images may be difficult for the model to interpret
- Text extraction may not be 100% accurate
- Large or complex images may take longer to analyze

## Next Steps

- [Smart Memory](smart-memory.md) - Persistent context
- [Document Management Tools](../tools/document-management.md) - Work with documents
- [Configuration](../getting-started/configuration.md) - Configure visual models
