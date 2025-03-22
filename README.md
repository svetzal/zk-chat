# 💬 Chat With Your Zettelkasten

This is a simple tool that lets you chat with a local "AI" that has access to the documents in your Zettelkasten. It will
index your markdown documents, and in your chat session it may choose to query your content, retrieve excerpts, read
entire documents, and generate responses based on the content in your Zettelkasten.

For "AI" it communicates with a local running instance of Ollama. Ollama must be installed and running for zkchat to
function.

## ✨ Features

- Command-line interface for quick access
- Graphical user interface for a more user-friendly experience
- RAG queries across your document base
- Interactive chat with context from your Zettelkasten
- Configurable LLM model selection
- Easy Zettelkasten folder configuration

### 🛠️ Tools

The chat interface provides access to several tools that enhance its capabilities:

- **Document Search Tools**
  - Find Documents: Locates relevant documents in your Zettelkasten based on your query
  - Find Excerpts: Retrieves specific passages from your documents that match your search criteria
  - Read Document: Accesses the full content of a specific document in your Zettelkasten
  - Write Document: Creates or updates documents in your Zettelkasten (requires --unsafe flag)

- **Smart Memory Tools**
  - Store Information: Saves important facts and context from conversations for future reference
  - Retrieve Information: Recalls previously stored information to provide more personalized responses

- **Available Tool Plugins**
  - [zk-rag-wikipedia](https://pypi.org/project/zk-rag-wikipedia/): A plugin for looking up information on Wikipedia and creating documents from the results

## 🔧 Requirements

You must have [ollama](https://ollama.com/) installed and running.

You must have a local knowledgebase / zettelkasten with content in markdown format. I
use [Obsidian](https://obsidian.md/), because I favour working locally, and I favour using the markdown format for
notes - because everything's local, and in plain text, I can simply point this tool at a Vault folder.

## 💻 Workstation setup

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

Optionally install tool plugins from PyPi:

```bash
pip install zk-rag-wikipedia
```

Setting up Ollama and installing a local model:

```bash
brew install ollama
ollama pull qwen2.5:14b
```

## 🚀 Usage

### 📟 Command-line Interface

Run `zkchat --vault /path/to/vault` to start the command-line interface.

Command-line options:
- `--vault PATH`: Specify the path to your Zettelkasten vault (required if no bookmarks are set)
- `--bookmark NAME`: Use a bookmarked vault path instead of specifying the path directly
- `--add-bookmark NAME PATH`: Add a new bookmark for a vault path
- `--remove-bookmark NAME`: Remove a bookmarked vault path
- `--list-bookmarks`: List all bookmarked vault paths
- `--model [model_name]`: Change the LLM model to use for chat
  - With model name: `zkchat --vault /path/to/vault --model llama2` - configure to use specified model
  - Without model name: `zkchat --vault /path/to/vault --model` - interactively select from available models
- `--reindex`: Reindex the Zettelkasten vault, will attempt to do so incrementally
- `--full`: Force full reindex (only used with --reindex)
- `--unsafe`: Enable operations that can write to your Zettelkasten. This flag is required for using tools that modify your Zettelkasten content, such as the Write Document tool. Use with caution as it allows the AI to make changes to your files.
- `--reset-memory`: Clear the smart memory storage

### 🧠 Smart Memory

The tool includes a Smart Memory mechanism that allows the AI to store and retrieve information during conversations. This memory:
- Persists between chat sessions
- Uses vector embeddings for semantic similarity search
- Enables the AI to recall previous context and information
- Can be cleared using the `--reset-memory` CLI option

### 🖥️ Graphical Interface (Experimental)

**_The GUI is experimental and may not work as expected. It is provided as a preview feature only._**

**Note:** The GUI has not yet been updated to use the new command-line vault path configuration. It still uses the old method of storing the configuration file in the user's home directory.

Run `zkchat-gui` to start the graphical interface. The GUI provides:

- A multi-line chat input for composing messages
- A scrollable chat history showing the entire conversation
- A resizable divider between chat history and input areas
- Settings menu (accessible via Settings -> Configure...) for:
  - Selecting the LLM model from available Ollama models
  - Configuring the Zettelkasten folder location
- Asynchronous chat responses that keep the interface responsive

When first run, both `zkchat` and `zkchat-gui` will need initial configuration:

For the command-line interface:
- You must provide the path to your Zettelkasten vault using the `--vault` argument
- You'll be prompted to select an LLM model from your Ollama installation (or you can specify it with `--model`)

For the GUI:
- You can configure these settings through the Settings menu

After initial configuration, the tool will start a full index build of your Zettelkasten.

### 📁 Storage Location

The tool stores its configuration and database in your Zettelkasten vault:
- `.zk_chat` - Configuration file stored in the vault root
- `.zk_chat_db/` - Chroma vector database folder stored in the vault root
