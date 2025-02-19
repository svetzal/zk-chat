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

I recommend you setting up a local virtual Python environment, to keep it clean, but you can install it globally.

```bash
pip install zk-rag
```

Run `zkchat` to start chatting.

When first run, `zkchat` will start the configuration. You will need to provide the path to your root Zettelkasten /
Obsidian vault folder, and the name of the LLM model you want to use in your Ollama installation. After configuration,
it will start a full index build of your Zettelkasten.
