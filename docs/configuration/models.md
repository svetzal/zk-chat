# Model Selection

Choosing the right model for your needs.

## Available Gateways

### Ollama (Local)

Run models locally on your machine.

**Advantages:**
- Complete privacy (no data sent to cloud)
- No API costs
- Works offline
- Full control over models

**Requirements:**
- Ollama installed and running
- Sufficient RAM/VRAM
- Compatible CPU/GPU

### OpenAI (Cloud)

Use OpenAI's hosted models.

**Advantages:**
- No local hardware requirements
- Latest GPT models
- Consistent performance
- Managed infrastructure

**Requirements:**
- OpenAI API key
- Internet connection
- API credits/subscription

## Ollama Models

### Recommended Models

For **36GB+ RAM:**

- **qwen2.5:14b** - Best balance of speed and capability
- **phi4:14b** - Fast and efficient
- **qwq:32b** - More capable, requires more resources

For **16-32GB RAM:**

- **qwen2.5:7b** - Good general purpose
- **phi3:3.8b** - Fast, less capable
- **llama3.2:3b** - Lightweight option

### Installing Ollama Models

```bash
# Pull a model
ollama pull qwen2.5:14b

# List installed models
ollama list

# Remove a model
ollama rm model-name
```

### Visual Analysis Models

For image analysis capabilities:

- **llava** - General purpose vision
- **bakllava** - Alternative vision model
- **llava-phi3** - Lightweight vision

```bash
ollama pull llava
```

## OpenAI Models

### Chat Models

- **gpt-4o** - Latest multimodal model
- **gpt-4-turbo** - Fast GPT-4 variant
- **gpt-3.5-turbo** - Cost-effective option

### Vision Models

- **gpt-4o** - Multimodal (text + vision)
- **gpt-4-vision-preview** - Older vision model

### Setting API Key

```bash
export OPENAI_API_KEY=your_api_key_here
```

## Model Selection Criteria

### By Task

**Document Search & RAG:**
- Medium models (7-14B parameters)
- Fast inference preferred
- Examples: qwen2.5:7b, phi4:14b

**Complex Reasoning:**
- Larger models (14B+ parameters)
- Better at multi-step problems
- Examples: qwen2.5:14b, qwq:32b

**Content Generation:**
- Medium to large models
- Good at following instructions
- Examples: qwen2.5:14b, gpt-4o

**Quick Queries:**
- Smaller, faster models
- Good for simple tasks
- Examples: phi3:3.8b, gpt-3.5-turbo

### By Hardware

**High-end (64GB+ RAM, GPU):**
- 32B+ parameter models
- Best quality responses
- Examples: qwq:32b, codestral

**Mid-range (36GB RAM, M1/M2 Mac):**
- 14B parameter models
- Good balance
- Examples: qwen2.5:14b, phi4:14b

**Entry-level (16GB RAM):**
- 7B or smaller models
- Faster, less capable
- Examples: qwen2.5:7b, phi3:3.8b

### By Cost

**Free (Ollama):**
- Local models
- One-time compute cost
- No ongoing fees

**Paid (OpenAI):**
- Per-token pricing
- No local resources needed
- Predictable quality

## Configuring Models

### First Run

When you first run zk-chat:

```bash
zk-chat interactive --vault /path/to/vault
```

You'll be prompted to select:
1. Gateway (ollama/openai)
2. Chat model
3. Visual model (optional)

### Changing Models

Specify model explicitly:

```bash
zk-chat interactive --model qwen2.5:14b
```

Or switch gateways:

```bash
zk-chat interactive --gateway openai --model gpt-4o
```

## Model Parameters

### Size

Number of parameters affects:
- **Quality** - Larger = better understanding
- **Speed** - Smaller = faster responses
- **Memory** - Larger = more RAM needed

### Context Window

How much text the model can process:
- **Small** - 2K-4K tokens
- **Medium** - 8K-16K tokens
- **Large** - 32K-128K tokens

Larger context windows help with:
- Reading long documents
- Maintaining conversation context
- Processing multiple documents

## Performance Tuning

### Ollama Optimization

**For faster responses:**
```bash
# Use smaller models
ollama pull phi3:3.8b

# Increase concurrency
export OLLAMA_NUM_PARALLEL=4
```

**For better quality:**
```bash
# Use larger models
ollama pull qwen2.5:14b

# More context
export OLLAMA_NUM_CTX=8192
```

### Resource Management

**Monitor usage:**
```bash
# Check running models
ollama ps

# System resources
htop  # or Activity Monitor on Mac
```

**Manage models:**
```bash
# Keep only needed models
ollama list
ollama rm unused-model
```

## Troubleshooting

### Model Not Found

**Error:** "Model not found"

**Solution:**
```bash
# Verify model is installed
ollama list

# Pull if missing
ollama pull model-name
```

### Out of Memory

**Error:** Model fails to load

**Solutions:**
- Use smaller model
- Close other applications
- Increase swap space
- Use OpenAI instead

### Slow Responses

**Causes:**
- Model too large for hardware
- System under load
- Network issues (OpenAI)

**Solutions:**
- Use smaller/faster model
- Free up resources
- Check internet connection

## Best Practices

1. **Start Small** - Begin with smaller models
2. **Test Performance** - Try different models for your use case
3. **Monitor Resources** - Watch RAM/CPU usage
4. **Keep Updated** - New models improve regularly
5. **Match Task** - Use appropriate model for task complexity

## See Also

- [Installation](../installation.md) - Initial setup
- [Configuration](vault.md) - Vault setup
- [Advanced Settings](advanced.md) - Fine-tuning
