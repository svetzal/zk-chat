# Chat With Your Zettelkasten

This is a simple tool that lets you chat with an "AI" that has access to the documents in your Zettelkasten. It will
index your markdown documents, and in your chat session it may choose to query your content, retrieve excerpts, read
entire documents, and generate responses based on the content in your Zettelkasten.

For "AI" it communicates with a local running instance of Ollama. Ollama must be installed and running for zkchat to
function.

## Features

- Command-line interface for quick access
- Graphical user interface for a more user-friendly experience
- RAG queries across your document base
- Interactive chat with context from your Zettelkasten
- Configurable LLM model selection
- Easy Zettelkasten folder configuration

## Requirements

You must have [ollama](https://ollama.com/) installed and running.

You must have a local knowledgebase / zettelkasten with content in markdown format. I
use [Obsidian](https://obsidian.md/), because I favour working locally, and I favour using the markdown format for
notes - because everything's local, and in plain text, I can simply point this tool at a Vault folder.

## Workstation setup

**_Right now, while this tool should run on Windows, we've only written instructions for Mac._**

I recommend you setting up a local virtual Python environment, to keep it clean, but you can install it globally.

Setting up a local environment, and activating it (recommended):

```bash
cd $HOME
python3 -mvenv .venv
source .venv/bin/activate
```

Installing the zk-rag module from PyPi:

```bash
pip install zk-rag
```

Setting up Ollama and installing a local model:

```bash
brew install ollama
ollama pull qwen2.5:14b
```

## Usage

### Command-line Interface

Run `zkchat` to start the command-line interface.

Command-line options:
- `--model [model_name]`: Change the LLM model to use for chat
  - With model name: `zkchat --model llama2` - configure to use specified model
  - Without model name: `zkchat --model` - interactively select from available models
- `--reindex`: Reindex the Zettelkasten vault, will attempt to do so incrementally
- `--full`: Force full reindex (only used with --reindex)
- `--unsafe`: Enable operations that can write to your Zettelkasten

### Graphical Interface

Run `zkchat-gui` to start the graphical interface. The GUI provides:

- A multi-line chat input for composing messages
- A scrollable chat history showing the entire conversation
- A resizable divider between chat history and input areas
- Settings menu (accessible via Settings -> Configure...) for:
  - Selecting the LLM model from available Ollama models
  - Configuring the Zettelkasten folder location
- Asynchronous chat responses that keep the interface responsive

When first run, both `zkchat` and `zkchat-gui` will prompt for initial configuration. You will need to provide:
- The path to your root Zettelkasten / Obsidian vault folder
- The LLM model you want to use from your Ollama installation

In the command-line interface, you'll be prompted for this information directly. In the GUI, you can configure these settings through the Settings menu. After initial configuration, the tool will start a full index build of your Zettelkasten.
