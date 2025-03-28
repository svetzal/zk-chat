# 💬 Chat With Your Zettelkasten

This is a simple tool that lets you chat with a local "AI" that has access to the documents in your Zettelkasten. It will
index your markdown documents, and in your chat session it may choose to query your content, retrieve excerpts, read
entire documents, and generate responses based on the content in your Zettelkasten.

For "AI" it communicates with either a local running instance of Ollama or OpenAI's API. By default, Ollama is used and must be installed and running for zkchat to function, but you can also configure it to use OpenAI with the `--gateway openai` option.

## ✨ Features

- Command-line interface for quick access
- (Experimental) Graphical user interface for a more user-friendly experience
- RAG queries across your document base
- Interactive chat with context from your Zettelkasten
- Configurable LLM model selection
- Easy Zettelkasten folder configuration

### 🛠️ Tools

The chat interface provides access to several tools that enhance its capabilities:

- **Document Management Tools**
  - Find Documents: Locates relevant documents in your Zettelkasten based on your query
  - Find Excerpts: Retrieves specific passages from your documents that match your search criteria
  - List Documents: Displays all documents in your Zettelkasten for easier navigation
  - Read Document: Accesses the full content of a specific document in your Zettelkasten
  - Write Document: Creates or updates documents in your Zettelkasten (requires --unsafe flag)
  - Rename Document: Changes the name of an existing document in your Zettelkasten (requires --unsafe flag)
  - Delete Document: Permanently removes a document from your Zettelkasten (requires --unsafe flag)

- **Smart Memory Tools**
  - Store Information: Saves important facts and context from conversations for future reference
  - Retrieve Information: Recalls previously stored information to provide more personalized responses

- **Git Integration Tools**
  - View Uncommitted Changes: Shows pending changes in your Zettelkasten vault
  - Commit Changes: Commits changes with AI-generated commit messages

- **Available Tool Plugins**
  - [zk-rag-wikipedia](https://pypi.org/project/zk-rag-wikipedia/): A plugin for looking up information on Wikipedia and creating documents from the results

## 🔧 Requirements

If using the default Ollama gateway, you must have [ollama](https://ollama.com/) installed and running.

If using the OpenAI gateway, you must have the OPENAI_API_KEY environment variable set with your OpenAI API key.

You must have a local knowledgebase / zettelkasten with content in markdown format. I
use [Obsidian](https://obsidian.md/), because I favour working locally, and I favour using the markdown format for
notes - because everything's local, and in plain text, I can simply point this tool at a Vault folder.

## 💻 Workstation setup

**_Right now, while this tool should run on Windows, but we've only written instructions for Mac._**

### Using pipx (recommended)

[pipx](https://pypa.github.io/pipx/) is a tool that allows you to install and run Python applications in isolated environments. It's ideal for end-user applications like zk-rag, as it keeps the application and its dependencies isolated from your system Python and other applications.

Installing pipx:

```bash
# On macOS
brew install pipx
pipx ensurepath

# On Linux
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Installing zk-rag with pipx:

```bash
pipx install zk-rag
```

Upgrading zk-rag with pipx:

```bash
pipx upgrade zk-rag
```

Installing plugins with pipx inject:

```bash
# Install the Wikipedia plugin
pipx inject zk-rag zk-rag-wikipedia
```

The benefit of using pipx is that it creates isolated environments for each application, avoiding dependency conflicts while still making the commands globally available.

### Alternative: Using a virtual environment

If you prefer more control over your Python environment, you can set up a local virtual environment:

Setting up a local environment, and activating it:

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

Setting up Ollama and installing a local model (if using the Ollama gateway):

```bash
brew install ollama
ollama pull qwen2.5:14b
```

Setting up OpenAI (if using the OpenAI gateway):

```bash
export OPENAI_API_KEY=your_api_key_here
```

## 🚀 Usage

### 📟 Command-line Interface

Run `zkchat --vault /path/to/vault` to start the command-line interface for the first time on a new vault.

If `zk-rag` hasn't been used with the vault before, it will prompt you for a model (using the default Ollama gateway) and perform a full index your vault before starting the chat.

Subsequently running `zkchat` on its own will launch it on the last opened vault, with the last selected model.

> If you want to allow the AI to make changes to your Zettelkasten, you must use the `--unsafe` flag. We highly recommend using `git` for version control if you enable this option.

> Specifying `--git` will initialize a new git repository for your vault if one doesn't already exist.

Command-line options:
- `--vault PATH`: Specify the path to your Zettelkasten vault (required if no bookmarks are set)
- `--bookmark NAME`: Use a bookmarked vault path instead of specifying the path directly
- `--add-bookmark NAME PATH`: Add a new bookmark for a vault path
- `--remove-bookmark NAME`: Remove a bookmarked vault path
- `--list-bookmarks`: List all bookmarked vault paths
- `--gateway {ollama,openai}`: Set the model gateway to use (ollama or openai). OpenAI requires OPENAI_API_KEY environment variable
- `--model [model_name]`: Change the LLM model to use for chat
  - With model name: `zkchat --vault /path/to/vault --model llama2` - configure to use specified model
  - Without model name: `zkchat --vault /path/to/vault --model` - interactively select from available models
- `--reindex`: Reindex the Zettelkasten vault, will attempt to do so incrementally
- `--full`: Force full reindex (only used with --reindex)
- `--unsafe`: Enable operations that can write to your Zettelkasten. This flag is required for using tools that modify your Zettelkasten content, such as the Write Document tool. Use with caution as it allows the AI to make changes to your files.
- `--reset-memory`: Clear the smart memory storage
- `--git`: Enable Git integration for version control of your Zettelkasten vault

#### Note on Models

For **local models** on Ollama, you're going to need to choose a model that fits in your available RAM (on MacOS) or in the VRAM on your GPU. The actual RAM used will vary based on many factors.

Our recommendation is a 14B to 28B parameter model like qwen2.5:14b or phi4:14b or even qwq:32b (if you don't run a lot of other programs at the same time) on a Macbook Pro M1 or later with 36GB of RAM or more.

The lower the number of parameters, the faster the model will be, but the less capable it will be. The higher the number of parameters, the slower the model will be, but the more capable it will be.

In general, newer models are more capable and more accurate. Certain models will be tuned for specific use cases. Read up on the models to understand what they're good at.

You will need to experiment to find the right balance for your system and use cases.

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
  - Selecting the LLM model from available models (based on the configured gateway)
  - Configuring the Zettelkasten folder location
- Asynchronous chat responses that keep the interface responsive

When first run, both `zkchat` and `zkchat-gui` will need initial configuration:

For the command-line interface:
- You must provide the path to your Zettelkasten vault using the `--vault` argument
- You can select which gateway to use (Ollama or OpenAI) with the `--gateway` argument
- You'll be prompted to select an LLM model from the available models for your chosen gateway (or you can specify it with `--model`)

For the GUI:
- You can configure these settings through the Settings menu

After initial configuration, the tool will start a full index build of your Zettelkasten.

### 📁 Storage Location

The tool stores its configuration and database in your Zettelkasten vault:
- `.zk_chat` - Configuration file stored in the vault root
- `.zk_chat_db/` - Chroma vector database folder stored in the vault root
