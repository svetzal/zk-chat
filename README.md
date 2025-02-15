# Query your Zettelkasten

This is a simple implementation of Retrieval Augmented Generation (RAG) for your Zettelkasten. It breaks your markdown
documents into chunks, and uses a cosine-distance query to place relevant text chunks from your Zettelkasten into an LLM
chat context in order to answer your questions.

It uses chromadb for a vector database (indexing the chunks, and doing distance queries for chunk selection) and ollama
in order to generate the responses.

This project has many limitations, it is simply a starting point upon which I am building a larger system. Treat it like
an example project, and build your own work on top of it.

## Limitations

- command-line only

That said, it includes all of the critical elements for doing RAG queries across a document base.

## Requirements

You must have [ollama](https://ollama.com/) installed and functional.

You must have a local knowledgebase / zettelkasten with content in markdown format. I
use [Obsidian](https://obsidian.md/), because I favour working locally, and I favour using the markdown format for
notes - because everything's local, and in plain text, I can simply point this tool at a Vault folder.

## Workstation setup

I recommend you setting up a local virtual Python environment, to keep it clean, but you can install it globally.

```bash
pip install zk-rag
```

Run `zk_reindex` to start the configuration. You will need to provide the path to your root Zettelkasten / Obsidian
vault folder, and the name of the LLM model you want to use in your Ollama installation. After configuration, it
will start a full index build of your Zettelkasten.

Run `zk_reindex` to re-index the contents of your zettelkasten at any time. As of v1.0.6 it will do an incremental
index, processing only documents that have changed since the last run.

Run `zk_chat` to query your Zettelkasten. As of v1.0.4 it will be a real chat, and it will remember the history of
your questions and the lookups it made within your Zettelkasten. Press enter (blank line) to exit the query loop.
