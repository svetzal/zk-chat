# Installation

This guide will walk you through installing Zk-Chat on your system.

## Requirements

Before installing Zk-Chat, you'll need:

- **Python 3.11 or later**
- **A Zettelkasten** with content in markdown format (e.g., an Obsidian vault)
- **LLM Backend** - one of:
    - [Ollama](https://ollama.com/) (recommended for local usage)
    - OpenAI API key (for cloud-based usage)

### Optional Requirements

- **For Visual Analysis**: A multimodal LLM model
    - Ollama: `llava`, `bakllava`, or similar
    - OpenAI: `gpt-4-vision` or similar
- **For Git Integration**: Git installed on your system

## Installation Methods

### Using pipx (Recommended)

[pipx](https://pypa.github.io/pipx/) is the recommended way to install Zk-Chat. It creates isolated environments for each application, avoiding dependency conflicts while making commands globally available.

#### Install pipx

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

=== "Windows"

    ```powershell
    python -m pip install --user pipx
    python -m pipx ensurepath
    ```

#### Install Zk-Chat

```bash
pipx install zk-chat
```

#### Upgrade Zk-Chat

```bash
pipx upgrade zk-chat
```

#### Install Plugins

```bash
# Install the Wikipedia plugin
pipx inject zk-chat zk-rag-wikipedia

# Install the Image Generator plugin
pipx inject zk-chat zk-rag-image-generator
```

### Using pip with Virtual Environment

If you prefer more control over your Python environment:

#### Create and Activate Virtual Environment

```bash
cd $HOME
python3 -m venv .venv
source .venv/bin/activate
```

#### Install Zk-Chat

```bash
pip install zk-chat
```

#### Install Plugins (Optional)

```bash
pip install zk-rag-wikipedia
pip install zk-rag-image-generator
```

## Setting Up LLM Backend

### Option 1: Ollama (Local)

Ollama is recommended for local, private usage.

#### Install Ollama

=== "macOS"

    ```bash
    brew install ollama
    ```

=== "Linux"

    Follow instructions at [ollama.com](https://ollama.com/)

=== "Windows"

    Download from [ollama.com](https://ollama.com/)

#### Download a Model

```bash
# Recommended models for different hardware configurations
ollama pull qwen2.5:14b      # For systems with 36GB+ RAM
ollama pull phi4:14b         # Alternative 14B model
ollama pull qwq:32b          # For systems with 64GB+ RAM
```

!!! tip "Model Selection"
    - **14B-28B parameters**: Recommended for most users with modern hardware
    - **Higher parameters**: Better capabilities but slower and more memory-intensive
    - **Newer models**: Generally more capable and accurate
    
    Experiment to find the right balance for your system and use cases.

#### Visual Models (Optional)

```bash
ollama pull llava           # For image analysis
```

### Option 2: OpenAI (Cloud)

For cloud-based usage with OpenAI's models.

#### Set API Key

```bash
export OPENAI_API_KEY=your_api_key_here
```

Add this to your shell profile (`.bashrc`, `.zshrc`, etc.) to make it permanent.

## Verify Installation

Check that Zk-Chat is installed correctly:

```bash
zk-chat --help
```

You should see the help message with available commands.

## Next Steps

- [Quick Start Guide](quick-start.md) - Get started with your first chat session
- [Configuration](configuration.md) - Learn about configuration options
- [Interactive Chat](../user-guide/interactive-chat.md) - Explore chat features
