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

### Recommended Models (2025)

For **64GB+ RAM (High-End Workstation):**

- **gpt-oss:120b** - Most capable, excellent for RAG and complex reasoning
- **qwen3:32b** - Latest generation, versatile across tasks
- **deepseek-r1:32b** - Advanced reasoning capabilities

For **36-48GB RAM (M2/M3 Mac, High-End PC):**

- **gpt-oss:20b** - Excellent balance of capability and performance
- **gemma3:27b** - Most capable single-GPU model with vision support
- **qwen3:14b** - Fast and capable, good for RAG tasks
- **phi-4:14b** - Microsoft's latest, efficient alternative

For **16-32GB RAM (Standard Mac/PC):**

- **qwen3:8b** - **Recommended** - Fast, versatile, excellent for RAG
- **qwen2.5:7b** - Proven alternative, very reliable
- **phi-4:14b** - Efficient on limited resources (if it fits)
- **mistral:7b** - Proven reliable performer

For **8-16GB RAM (Entry Level):**

- **qwen3:1.5b** - Lightweight but capable
- **qwen2.5:3b** - Good balance for limited resources
- **phi-4:3b** - Fast for simple tasks
- **gemma3:2b** - Minimal resource usage

### Installing Ollama Models

```bash
# Pull a model
ollama pull qwen3:8b

# List installed models
ollama list

# Remove a model
ollama rm model-name
```

### Visual Analysis Models (2025)

For image analysis and multimodal capabilities:

**High Quality (36GB+ RAM):**
- **gemma3:27b** - **Recommended** - Excellent vision with manageable resources
- **qwen3-vl:32b** - Most powerful in Qwen family for vision
- **llama3.2-vision:90b** - Alternative option (requires 64GB+ RAM)

**Balanced (16-32GB RAM):**
- **gemma3:9b** - Good vision quality, reasonable resources
- **qwen3-vl:8b** - Fast and capable
- **llama3.2-vision:11b** - Alternative balanced option

**Lightweight (8-16GB RAM):**
- **gemma3:2b** - Fast inference with vision
- **llava:7b** - Fallback option for very limited resources
- **llava-phi3** - Efficient for minimal hardware

```bash
# Install a vision model
ollama pull gemma3:27b
```

## OpenAI Models

### Chat Models

- **gpt-5** - Latest multimodal model
- **gpt-4.1** - Fast GPT-4 variant
- **gpt-4o** - Cost-effective option

### Vision Models

- **gpt-5** - Latest multimodal model
- **gpt-4.1** - Fast GPT-4 variant
- **gpt-4o** - Cost-effective option

### Setting API Key

```bash
export OPENAI_API_KEY=your_api_key_here
```

## Model Selection Criteria

### By Task

**Document Search & RAG:**
- Medium models (7-14B parameters)
- Fast inference preferred
- Examples: **qwen3:8b**, qwen2.5:7b, gpt-oss:20b

**Complex Reasoning:**
- Larger models (14B+ parameters)
- Better at multi-step problems
- Examples: **gpt-oss:120b**, deepseek-r1:32b, qwen3:14b

**Content Generation:**
- Medium to large models
- Good at following instructions
- Examples: **qwen3:14b**, gpt-oss:20b, gpt-4o

**Visual Analysis:**
- Vision-capable models
- Multimodal understanding
- Examples: **gemma3:27b**, qwen3-vl:8b, gemma3:9b

**Quick Queries:**
- Smaller, faster models
- Good for simple tasks
- Examples: **qwen3:1.5b**, qwen2.5:3b, gemma3:2b

### By Hardware

**High-end (64GB+ RAM, GPU):**
- 32B+ parameter models
- Best quality responses
- Examples: **gpt-oss:120b**, qwen3:32b, deepseek-r1:32b

**Mid-range (36-48GB RAM, M2/M3 Mac):**
- 14-27B parameter models
- Excellent balance
- Examples: **gpt-oss:20b**, gemma3:27b, qwen3:14b

**Entry-level (16-32GB RAM):**
- 7-8B models
- Good for most tasks
- Examples: **qwen3:8b**, qwen2.5:7b, mistral:7b

**Resource-constrained (8-16GB RAM):**
- 3B or smaller models
- Basic capabilities
- Examples: **qwen3:1.5b**, qwen2.5:3b, gemma3:2b

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
zk-chat interactive --model qwen3:8b
```

With visual model:

```bash
zk-chat interactive --model qwen3:14b --visual-model gemma3:27b
```

High-end setup:

```bash
zk-chat interactive --model gpt-oss:20b --visual-model gemma3:27b
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
ollama pull qwen3:1.5b

# Increase concurrency
export OLLAMA_NUM_PARALLEL=4
```

**For better quality:**
```bash
# Best RAG performance
ollama pull gpt-oss:20b

# Or balanced option
ollama pull qwen3:14b

# More context (for long documents)
export OLLAMA_NUM_CTX=16384
```

**For vision tasks:**
```bash
# Best vision model
ollama pull gemma3:27b

# Or lighter option
ollama pull gemma3:9b
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
