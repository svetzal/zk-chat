# Graphical User Interface (GUI)

!!! warning "Experimental Feature"
    The GUI is experimental and may not have all features available in the CLI. It uses an older configuration system and is provided as a preview.

## Launching the GUI

```bash
zk-chat gui launch
```

## Interface Overview

The GUI provides:

- **Multi-line chat input** - Compose longer messages
- **Scrollable chat history** - View entire conversation
- **Resizable panels** - Adjust layout to your preference
- **Settings menu** - Configure models and vault location

## Main Components

### Chat History Panel

Located in the upper portion of the window:
- Shows your messages and AI responses
- Scrollable for long conversations
- Auto-scrolls to latest message

### Input Panel

Located in the lower portion:
- Multi-line text input
- Send button to submit messages
- Resizable using the divider

### Menu Bar

**Settings → Configure...**
- Select chat model
- Select visual model (or disable)
- Set Zettelkasten folder location

## First-Time Setup

When you first launch the GUI:

1. Click **Settings → Configure...**
2. Set your Zettelkasten folder location
3. Select a chat model from available models
4. Optionally select a visual analysis model
5. Click OK/Apply

The GUI will then build an initial index of your vault.

## Using the GUI

### Sending Messages

1. Type your message in the input panel
2. Click Send or press Ctrl+Enter
3. Wait for AI response

### Viewing History

- Scroll through the chat history panel
- All messages persist during the session

### Resizing Panels

- Drag the divider between history and input
- Adjust to your preferred layout

## Features

### What Works

✅ Basic chat functionality
✅ Document search
✅ Reading documents
✅ Visual analysis (if configured)
✅ Tool usage display

### Current Limitations

❌ No agent mode
❌ No file modification support
❌ Uses legacy configuration
❌ Limited command options
❌ No smart memory reset

## Configuration

The GUI stores its configuration in:
```
~/.zk_chat_gui
```

This is separate from the CLI configuration stored in your vault.

## Tips for GUI Usage

1. **Use CLI for Setup**: Configure with CLI first
2. **Simple Queries**: GUI works best for straightforward questions
3. **Complex Tasks**: Use CLI for advanced features
4. **Testing**: Use GUI to preview functionality

## Troubleshooting

### GUI Won't Launch

**Check:**
- Python PySide6 is installed
- Display environment is available
- No conflicting processes

**Try:**
```bash
# Reinstall GUI dependencies
pip install --force-reinstall PySide6
```

### Can't Set Vault Location

**Issue:** Settings don't persist

**Solution:**
- Ensure write permissions to home directory
- Check `~/.zk_chat_gui` exists and is writable

### Models Not Appearing

**Issue:** No models in dropdown

**Check:**
- Ollama is running: `ollama list`
- OpenAI key is set (if using OpenAI)

## Migration to CLI

For full functionality, we recommend using the CLI:

```bash
# Instead of GUI
zk-chat gui launch

# Use CLI
zk-chat interactive
```

The CLI offers:
- Agent mode
- File modification with Git
- Full feature set
- Better error handling
- More configuration options

## Future Development

The GUI is undergoing active development to:
- Match CLI feature parity
- Use same configuration system
- Add advanced features
- Improve user experience

## See Also

- [Command Line Interface](cli.md) - Full-featured CLI
- [Interactive Chat](interactive-chat.md) - CLI chat features
- [Installation](../installation.md) - Setup guide
