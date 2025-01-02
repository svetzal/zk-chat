# Query your Zettelkasten

This is a simple implementation of Retrieval Augmented Generation (RAG) for your Zettelkasten. It breaks your markdown
documents into chunks, and uses a cosine-distance query to place relevant text chunks from your Zettelkasten into an LLM
chat context in order to answer your questions.

It uses chromadb for a vector database (indexing the chunks, and doing distance queries for chunk selection) and ollama
in order to generate the responses.

This project has many limitations, it is simply a starting point upon which I am building a larger system. Treat it like
an example project, and build your own work on top of it.

Limitations:
- no chat history
- requires tweaking python code to run on your system
- command-line only

That said, it includes all of the critical elements for doing RAG queries across a document base.

## Workstation setup

I recommend you setting up a local virtual Python environment, to keep it clean.

```bash
python3 -mvenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Adjust `settings.py` to point to your Zettelkasten directory, and the model you want to use in your ollama installation.
Use `ollama list` to check which ones you have set up.

Run `python zk_reindex.py` to re-index the contents of your zettelkasten.

Run `python zk_query.py` to query your Zettelkasten. Note that this is not a true chat, it will not take into account
the history of your queries, every query is answered as a stand-alone question.
