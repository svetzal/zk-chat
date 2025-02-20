# Chat With Your Zettelkasten

This is a simple tool that lets you chat with an "AI" that has access to the documents in your Zettelkasten. It will
index your markdown documents, and in your chat session it may choose to query your content, retrieve excerpts, read
entire documents, and generate responses based on the content in your Zettelkasten.

For "AI" it communicates with a local running instance of Ollama. Ollama must be installed and running for zkchat to
function.

## Limitations

- command-line only

That said, it includes all of the critical elements for doing RAG queries across a document base.

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

Run `zkchat` to start chatting.

Command-line options:
- `--model [model_name]`: Change the LLM model to use for chat
  - With model name: `zkchat --model llama2` - configure to use specified model
  - Without model name: `zkchat --model` - interactively select from available models
- `--reindex`: Reindex the Zettelkasten vault, will attempt to do so incrementally
- `--full`: Force full reindex (only used with --reindex)
- `--unsafe`: Enable operations that can write to your Zettelkasten

When first run, `zkchat` will start the configuration. You will need to provide the path to your root Zettelkasten /
Obsidian vault folder, and the name of the LLM model you want to use in your Ollama installation. After configuration,
it will start a full index build of your Zettelkasten.
