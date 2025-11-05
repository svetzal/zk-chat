# Visual Analysis

Visual analysis enables the AI to examine and describe images in your Zettelkasten.

## Setup

### Requirements

1. **Visual model configured** - A model capable of image analysis
2. **Images in your vault** - PNG, JPEG, GIF, or other common formats

### Configuring a Visual Model

During setup, when asked:
```
Do you want to enable visual analysis? (y/n):
```

Type `y` and select a vision-capable model:

**For Ollama:**
- `llava` - LLaVA vision model
- `bakllava` - BakLLaVA variant
- `llava-phi3` - Phi-based variant

**For OpenAI:**
- `gpt-4-vision-preview` - GPT-4 with vision
- `gpt-4o` - Multimodal GPT-4

## Using Visual Analysis

### Analyzing Images

Simply ask about an image:

```
You: What's in the image at diagrams/architecture.png?

AI: Using tool: analyze_image
Path: diagrams/architecture.png

The image shows a system architecture diagram depicting three main layers:
1. Frontend - React-based web application
2. Backend API - Node.js services
3. Database - PostgreSQL with Redis cache
...
```

### Common Use Cases

**Diagram Analysis**
```
You: Describe the flowchart in process-diagram.png
```

**Photo Description**
```
You: What does the whiteboard photo show?
```

**Chart Interpretation**
```
You: Analyze the graph in sales-data-2024.jpg
```

**Text Extraction**
```
You: What text is in the screenshot?
```

## Supported Formats

- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- GIF (`.gif`)
- WebP (`.webp`)
- BMP (`.bmp`)

## Image Paths

Images can be referenced:

**Relative to vault:**
```
assets/diagram.png
images/photo.jpg
attachments/screenshot.png
```

**In subdirectories:**
```
projects/project-a/wireframes/design.png
notes/embedded-image.jpg
```

## Best Practices

1. **Be specific** - Ask clear questions about what you want to know
2. **Good organization** - Keep images in logical folders
3. **Descriptive names** - Use meaningful filenames
4. **Ask follow-ups** - Request more details if needed

## Example Workflow

```
You: What diagrams do I have in my vault?

AI: [Lists image files]
Found 5 diagrams:
- architecture.png
- dataflow.png
- ui-mockup.png
...

You: Describe the architecture diagram

AI: Using tool: analyze_image
[Provides detailed description]

You: How does this relate to my implementation notes?

AI: Using tool: find_documents
Query: architecture implementation
[Finds related documents and explains connections]
```

## Limitations

- **Model dependent** - Quality varies by model
- **Complex images** - May struggle with very detailed diagrams
- **Text readability** - Small text may not be readable
- **File size** - Large images may take longer to process

## Troubleshooting

### No Visual Model Available

**Error:** "Visual analysis not configured"

**Solution:**
```bash
# Reconfigure and select a visual model
zk-chat interactive
# Follow prompts to select visual model
```

### Image Not Found

**Error:** "Image not found at path"

**Check:**
- File exists in vault
- Path is correct (relative to vault root)
- File extension is supported

### Poor Results

**Try:**
- Use a different visual model
- Ensure image quality is good
- Ask more specific questions
- Describe what you're looking for

## See Also

- [Available Tools](tools.md) - All tool capabilities
- [Model Selection](../configuration/models.md) - Choosing models
