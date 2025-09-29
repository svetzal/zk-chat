# 💬 Chat With Your Zettelkasten

This is a simple tool that lets you chat with an "AI" that has access to the documents in your Zettelkasten. It will
index your markdown documents, and in your chat session it may choose to query your content, retrieve excerpts, read
entire documents, and generate responses based on the content in your Zettelkasten.

For "AI" it communicates with either a local running instance of Ollama or OpenAI's API. By default, Ollama is used and must be installed and running for zk-chat to function, but you can also configure it to use OpenAI with the `--gateway openai` option.

## ✨ Features

- Command-line interface for quick access
- (Experimental) Graphical user interface for a more user-friendly experience
- RAG queries across your document base
- Interactive chat with context from your Zettelkasten
- Configurable LLM model selection
- Optional visual analysis capability for images in your Zettelkasten
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

- **Visual Analysis Tools**
  - Analyze Image: Examines and describes the content of images in your Zettelkasten (requires a visual model to be configured)

- **Navigation Tools**
  - Resolve WikiLink: Converts wikilinks (e.g., [[Document Title]]) to relative file paths for navigation between documents

- **Graph Traversal Tools** 🆕
  - Extract Wikilinks: Fast extraction of all wikilinks from documents with line numbers and context
  - Find Backlinks: Discover what documents link TO a target document (reverse navigation)
  - Find Forward Links: Discover what documents a source document links TO (forward navigation)
  - Link Path Finding: Find connection paths between documents through wikilinks
  - Link Metrics: Analyze connectivity patterns and identify hub documents

- **Smart Memory Tools**
  - Store Information: Saves important facts and context from conversations for future reference
  - Retrieve Information: Recalls previously stored information to provide more personalized responses

- **Git Integration Tools**
  - View Uncommitted Changes: Shows pending changes in your Zettelkasten vault
  - Commit Changes: Commits changes with AI-generated commit messages

- **Available Tool Plugins**
  - [zk-rag-wikipedia](https://pypi.org/project/zk-rag-wikipedia/): A plugin for looking up information on Wikipedia and creating documents from the results
  - [zk-rag-image-generator](https://pypi.org/project/zk-rag-image-generator/): A plugin for generating images using Stable Diffusion 3.5 Medium

### 🔌 Plugin Development

Zk-Chat supports a rich plugin architecture that allows developers to extend the chat agent with custom tools. See [PLUGINS.md](PLUGINS.md) for a comprehensive guide on developing plugins that integrate with the zk-chat runtime environment.

## 🔧 Requirements

If using the default Ollama gateway, you must have [ollama](https://ollama.com/) installed and running.

If using the OpenAI gateway, you must have the OPENAI_API_KEY environment variable set with your OpenAI API key.

For visual analysis capabilities, you need a model that supports image analysis:
- For Ollama: models like llava, bakllava, or other multimodal models
- For OpenAI: models like gpt-4-vision or other vision-capable models

You must have a local knowledgebase / zettelkasten with content in markdown format. I
use [Obsidian](https://obsidian.md/), because I favour working locally, and I favour using the markdown format for
notes - because everything's local, and in plain text, I can simply point this tool at a Vault folder.

## 💻 Workstation setup

**_Right now, while this tool should run on Windows, but we've only written instructions for Mac._**

### Using pipx (recommended)

[pipx](https://pypa.github.io/pipx/) is a tool that allows you to install and run Python applications in isolated environments. It's ideal for end-user applications like zk-chat, as it keeps the application and its dependencies isolated from your system Python and other applications.

Installing pipx:

```bash
# On macOS
brew install pipx
pipx ensurepath

# On Linux
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Installing zk-chat with pipx:

```bash
pipx install zk-chat
```

Upgrading zk-chat with pipx:

```bash
pipx upgrade zk-chat
```

Installing plugins with pipx inject:

```bash
# Install the Wikipedia plugin
pipx inject zk-chat zk-rag-wikipedia
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

Installing the zk-chat module from PyPi:

```bash
pip install zk-chat
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

The CLI uses a modern command-based interface. Use `zk-chat --help` to see all available commands.

#### 💬 Interactive Chat

Start an interactive chat session with your Zettelkasten:

```bash
# First time with a new vault
zk-chat interactive --vault /path/to/vault

# Subsequent uses (remembers last vault)
zk-chat interactive

# Use autonomous agent mode for complex tasks
zk-chat interactive --agent

# Allow AI to modify files (use with caution!)
zk-chat interactive --unsafe --git
```

If `zk-chat` hasn't been used with the vault before, it will prompt you for:
1. A chat model (using the default Ollama gateway)
2. Whether you want to select a visual analysis model (optional)

It will then perform a full index of your vault before starting the chat.

#### ❓ Single Query

Ask a single question without starting an interactive session:

```bash
# Ask a question directly
zk-chat query "What are my thoughts on productivity?"

# Read question from a file
cat prompt.txt | zk-chat query

# Use agent mode for complex queries
zk-chat query "Find all related concepts" --agent
```

#### 🖥️ Graphical Interface

Launch the experimental GUI:

```bash
zk-chat gui launch
```

**Note:** The GUI is experimental and uses an older configuration system.

#### 🔍 Index Management

Manage your Zettelkasten search index:

```bash
# Rebuild index (incremental - fast)
zk-chat index rebuild

# Full rebuild (comprehensive - slower)
zk-chat index rebuild --full

# Check index status
zk-chat index status
```

#### 📚 Vault and Bookmark Management

The CLI supports bookmarking vault paths for easy access:

```bash
# Save current vault as bookmark
zk-chat interactive --vault /path/to/vault --save

# List all bookmarks
zk-chat interactive --list-bookmarks

# Remove a bookmark
zk-chat interactive --remove-bookmark /path/to/vault
```

#### ⚙️ Command Options

**Common options available across commands:**

- `--vault PATH` / `-v PATH`: Specify the path to your Zettelkasten vault
- `--gateway {ollama,openai}` / `-g`: Set the model gateway (requires OPENAI_API_KEY for OpenAI)
- `--model MODEL` / `-m`: Set the chat model to use
- `--visual-model MODEL`: Set the visual analysis model (optional)

**Interactive chat specific options:**

- `--agent`: Use autonomous agent mode for complex problem-solving
- `--unsafe`: Allow AI to modify your Zettelkasten files (use with caution!)
- `--git`: Enable Git integration for version control
- `--store-prompt` / `--no-store-prompt`: Control whether system prompt is stored in vault
- `--reindex`: Rebuild index before starting chat
- `--full`: Force full reindex (use with --reindex)
- `--reset-memory`: Clear the smart memory storage
- `--save`: Save the vault path as a bookmark
- `--remove-bookmark PATH`: Remove a bookmarked vault path
- `--list-bookmarks`: List all bookmarked vault paths

> **⚠️ Safety Note:** If you want to allow the AI to make changes to your Zettelkasten, you must use the `--unsafe` flag. We highly recommend using `--git` for version control if you enable this option.

> **📁 Git Integration:** Specifying `--git` will initialize a new git repository for your vault if one doesn't already exist.

#### Note on Models

For **local models** on Ollama, you're going to need to choose a model that fits in your available RAM (on MacOS) or in the VRAM on your GPU. The actual RAM used will vary based on many factors.

Our recommendation is a 14B to 28B parameter model like qwen2.5:14b or phi4:14b or even qwq:32b (if you don't run a lot of other programs at the same time) on a Macbook Pro M1 or later with 36GB of RAM or more.

The lower the number of parameters, the faster the model will be, but the less capable it will be. The higher the number of parameters, the slower the model will be, but the more capable it will be.

In general, newer models are more capable and more accurate. Certain models will be tuned for specific use cases. Read up on the models to understand what they're good at.

You will need to experiment to find the right balance for your system and use cases.

### 🖼️ Visual Analysis

If you've configured a visual analysis model, you can analyze images in your Zettelkasten by asking the AI about them. For example:
- "What's in the image at images/diagram.png?"
- "Can you describe the chart in assets/sales-data.jpg?"
- "Analyze the photo in attachments/meeting-whiteboard.png"

The AI will use the configured visual model to analyze the image and provide a description of its contents. This is particularly useful for:
- Understanding diagrams and charts in your notes
- Extracting text from images
- Getting descriptions of visual content for reference
- Analyzing screenshots or photos you've added to your knowledge base

Note: Visual analysis is only available if you've configured a visual model during setup.

### 🧠 Smart Memory

The tool includes a Smart Memory mechanism that allows the AI to store and retrieve information during conversations. This memory:
- Persists between chat sessions
- Uses vector embeddings for semantic similarity search
- Enables the AI to recall previous context and information
- Can be cleared using the `--reset-memory` CLI option

### 🖥️ Graphical Interface (Experimental)

**_The GUI is experimental and may not work as expected. It is provided as a preview feature only._**

**Note:** The GUI has not yet been updated to use the new command-line vault path configuration. It still uses the old method of storing the configuration file in the user's home directory.

Run `zk-chat gui launch` to start the graphical interface. The GUI provides:

- A multi-line chat input for composing messages
- A scrollable chat history showing the entire conversation
- A resizable divider between chat history and input areas
- Settings menu (accessible via Settings -> Configure...) for:
  - Selecting the LLM model for chat from available models (based on the configured gateway)
  - Selecting an optional visual analysis model or disabling visual analysis
  - Configuring the Zettelkasten folder location
- Asynchronous chat responses that keep the interface responsive

When first run, both `zk-chat interactive` and `zk-chat gui launch` will need initial configuration:

For the command-line interface:
- You must provide the path to your Zettelkasten vault using the `--vault` argument
- You can select which gateway to use (Ollama or OpenAI) with the `--gateway` argument
- You'll be prompted to select an LLM model for chat from the available models for your chosen gateway (or you can specify it with `--model`)
- You'll be asked if you want to select a visual analysis model (optional)

For the GUI:
- You can configure these settings through the Settings menu
- You can enable or disable visual analysis by selecting a model or choosing "None - Disable Visual Analysis"

After initial configuration, the tool will start a full index build of your Zettelkasten.

### 📁 Storage Location

The tool stores its configuration and database in your Zettelkasten vault:
- `.zk_chat` - Configuration file stored in the vault root
- `.zk_chat_db/` - Chroma vector database folder stored in the vault root
- `ZkSystemPrompt.md` - System prompt file created in the vault root if it doesn't exist. This file defines the behavior of the AI assistant and can be customized to change how the assistant interacts with your Zettelkasten. By default, this file is created and used. You can prevent the creation of this file by not using the `--store-prompt` parameter, in which case the default system prompt will be used.
