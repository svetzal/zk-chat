# Installation

This guide will help you install zk-chat on your system.

## System Requirements

- **Python**: 3.11 or higher
- **Operating System**: macOS, Linux (Windows support is experimental)
- **LLM Backend**: Either [Ollama](https://ollama.com/) (local) or OpenAI API access

## Prerequisites

### For Local LLM (Ollama - Recommended)

If you want to use local AI models, you'll need to install Ollama:

=== "macOS"

    ```bash
    brew install ollama
    ```

=== "Linux"

    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```

After installing Ollama, pull a model:

```bash
ollama pull qwen2.5:14b
```

!!! tip "Model Recommendations"
    For best results with 36GB+ RAM, we recommend:
    
    - `qwen2.5:14b` - Good balance of speed and capability
    - `phi4:14b` - Fast and efficient
    - `qwq:32b` - More capable, requires more RAM

### For OpenAI API

If you prefer to use OpenAI's API instead of local models:

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Set the environment variable:

```bash
export OPENAI_API_KEY=your_api_key_here
```

## Installation Methods

### Method 1: Using pipx (Recommended)

[pipx](https://pypa.github.io/pipx/) installs Python applications in isolated environments, preventing dependency conflicts.

**Install pipx:**

=== "macOS"

    ```bash
    brew install pipx
    pipx ensurepath
    ```

=== "Linux"

    ```bash
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    ```

**Install zk-chat:**

```bash
pipx install zk-chat
```

**Upgrade zk-chat:**

```bash
pipx upgrade zk-chat
```

**Install plugins:**

```bash
# Example: Wikipedia plugin
pipx inject zk-chat zk-rag-wikipedia

# Example: Image generator plugin
pipx inject zk-chat zk-rag-image-generator
```

### Method 2: Using pip in a Virtual Environment

If you prefer managing your own virtual environment:

**Create and activate a virtual environment:**

```bash
cd $HOME
python3 -m venv .venv
source .venv/bin/activate
```

**Install zk-chat:**

```bash
pip install zk-chat
```

**Install plugins (optional):**

```bash
pip install zk-rag-wikipedia
pip install zk-rag-image-generator
```

## Verify Installation

Verify that zk-chat is installed correctly:

```bash
zk-chat --help
```

You should see the command-line help output with available commands.

## First-Time Setup

When you first run zk-chat, you'll need to provide:

1. **Vault Path**: The location of your Zettelkasten folder
2. **Model Selection**: Choose an LLM model for chat
3. **Visual Model** (optional): Choose a model for image analysis

Example first run:

```bash
zk-chat interactive --vault /path/to/your/vault
```

The tool will:

1. Prompt you to select a chat model
2. Ask if you want visual analysis capabilities
3. Build an initial index of your documents

!!! note "Index Building"
    The first index build may take a few minutes depending on the size of your Zettelkasten.

## Next Steps

- Read the [Quick Start Guide](quick-start.md) for a hands-on tutorial
- Explore [Command Line Interface](usage/cli.md) for detailed command reference
- Learn about [Available Tools](features/tools.md) to understand what the AI can do

## Troubleshooting

### Ollama Connection Issues

If zk-chat can't connect to Ollama:

1. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

2. Check that the model is available:
   ```bash
   ollama list
   ```

### Import Errors

If you encounter import errors, ensure you have the correct Python version:

```bash
python --version  # Should be 3.11 or higher
```

### Permission Issues

If you get permission errors during installation:

- Use `pipx` instead of system-wide pip installation
- Or create a virtual environment as shown in Method 2
