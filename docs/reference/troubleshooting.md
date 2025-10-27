# Troubleshooting

Common issues and solutions for Zk-Chat.

## Installation Issues

### pip install fails

**Symptom:** `pip install zk-chat` fails with errors.

**Solutions:**

1. Ensure Python 3.11 or later:
   ```bash
   python3 --version
   ```

2. Upgrade pip:
   ```bash
   pip install --upgrade pip
   ```

3. Use pipx instead:
   ```bash
   pipx install zk-chat
   ```

### Command not found after installation

**Symptom:** `zk-chat: command not found`

**Solutions:**

1. With pipx, ensure path is configured:
   ```bash
   pipx ensurepath
   ```

2. Restart your shell or run:
   ```bash
   source ~/.bashrc  # or ~/.zshrc
   ```

## Connection Issues

### Ollama connection failed

**Symptom:** "Failed to connect to Ollama"

**Solutions:**

1. Check if Ollama is running:
   ```bash
   ollama list
   ```

2. Start Ollama:
   ```bash
   ollama serve
   ```

3. Verify Ollama is accessible:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### OpenAI API key issues

**Symptom:** "OpenAI API key not found" or authentication errors

**Solutions:**

1. Set environment variable:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

2. Add to shell profile for persistence:
   ```bash
   echo 'export OPENAI_API_KEY=your_api_key' >> ~/.bashrc
   ```

3. Verify it's set:
   ```bash
   echo $OPENAI_API_KEY
   ```

## Index Issues

### Index build fails

**Symptom:** Index build stops with errors.

**Solutions:**

1. Check disk space:
   ```bash
   df -h
   ```

2. Verify vault path is correct:
   ```bash
   ls /path/to/vault
   ```

3. Try full rebuild:
   ```bash
   zk-chat index rebuild --full
   ```

4. Delete and rebuild:
   ```bash
   rm -rf /path/to/vault/.zk_chat_db
   zk-chat index rebuild --full
   ```

### Search not finding documents

**Symptom:** Known documents not appearing in search results.

**Solutions:**

1. Rebuild index:
   ```bash
   zk-chat index rebuild
   ```

2. Verify file is markdown:
   - Must have `.md` extension
   - Must be in vault directory

3. Check file permissions:
   ```bash
   ls -la /path/to/vault
   ```

4. Try full rebuild:
   ```bash
   zk-chat index rebuild --full
   ```

## Performance Issues

### Slow responses

**Symptom:** AI takes a long time to respond.

**Solutions:**

1. Use a smaller/faster model:
   ```bash
   zk-chat interactive --model phi4:14b
   ```

2. Check system resources:
   ```bash
   htop  # or top
   ```

3. Close other applications

4. For large vaults, ensure index is current:
   ```bash
   zk-chat index rebuild
   ```

### High memory usage

**Symptom:** System running out of memory.

**Solutions:**

1. Use smaller models:
   - 7B parameters instead of 14B+
   
2. Close other applications

3. For Ollama, check running models:
   ```bash
   ollama ps
   ```

4. Stop unused models:
   ```bash
   ollama stop <model-name>
   ```

## Chat Issues

### Chat not responding

**Symptom:** Chat session hangs or doesn't respond.

**Solutions:**

1. Check Ollama/OpenAI connection

2. Restart chat session:
   - Press Ctrl+C to exit
   - Start new session

3. Check for errors in output

4. Try simpler query

### AI giving incorrect information

**Symptom:** AI provides information not in your vault.

**Solutions:**

1. Be more specific in queries:
   ```
   "Based on my documents, what..."
   ```

2. Ask for sources:
   ```
   "What documents did you use to answer that?"
   ```

3. Rebuild index if documents were recently added

4. Customize system prompt to emphasize vault-only responses

### Tools not working

**Symptom:** AI says tools are unavailable or failing.

**Solutions:**

1. For write tools, check `--unsafe` flag:
   ```bash
   zk-chat interactive --unsafe --git
   ```

2. For Git tools, check `--git` flag:
   ```bash
   zk-chat interactive --git
   ```

3. Verify vault permissions

4. Check tool-specific requirements

## Configuration Issues

### Configuration not persisting

**Symptom:** Settings reset between sessions.

**Solutions:**

1. Check `.zk_chat` file exists:
   ```bash
   ls -la /path/to/vault/.zk_chat
   ```

2. Verify file permissions:
   ```bash
   chmod 644 /path/to/vault/.zk_chat
   ```

3. Ensure vault path is consistent

### MCP servers not loading

**Symptom:** Registered MCP servers not available.

**Solutions:**

1. List servers:
   ```bash
   zk-chat mcp list
   ```

2. Verify availability:
   ```bash
   zk-chat mcp verify
   ```

3. Check server command/URL is correct

4. Re-add server:
   ```bash
   zk-chat mcp remove server-name
   zk-chat mcp add server-name --type stdio --command command
   ```

## Plugin Issues

### Plugins not loading

**Symptom:** Installed plugins not available.

**Solutions:**

1. Verify plugin is installed:
   ```bash
   pip list | grep zk-rag
   ```

2. Check entry points:
   ```bash
   pip show zk-rag-wikipedia
   ```

3. Reinstall plugin:
   ```bash
   pip uninstall zk-rag-wikipedia
   pip install zk-rag-wikipedia
   ```

4. Check for errors at startup

## GUI Issues

### GUI won't start

**Symptom:** `zk-chat gui launch` fails.

**Solutions:**

1. Check PySide6 is installed:
   ```bash
   pip list | grep PySide6
   ```

2. Install/reinstall GUI dependencies:
   ```bash
   pip install --upgrade zk-chat
   ```

3. Check display environment (on remote systems)

4. Try CLI instead - GUI is experimental

## File Permission Issues

### Cannot write to vault

**Symptom:** File operations fail with permission errors.

**Solutions:**

1. Check vault ownership:
   ```bash
   ls -la /path/to/vault
   ```

2. Fix permissions:
   ```bash
   chmod -R u+w /path/to/vault
   ```

3. Ensure you're not running as wrong user

## Git Integration Issues

### Git commands failing

**Symptom:** Git tools report errors.

**Solutions:**

1. Verify Git is installed:
   ```bash
   git --version
   ```

2. Check repository state:
   ```bash
   cd /path/to/vault
   git status
   ```

3. Initialize manually if needed:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

4. Resolve conflicts manually

## Getting Help

If these solutions don't help:

1. **Check GitHub Issues**: [zk-chat issues](https://github.com/svetzal/zk-chat/issues)

2. **Create New Issue**: Include:
   - Zk-Chat version: `pip show zk-chat`
   - Python version: `python --version`
   - Operating system
   - Error messages
   - Steps to reproduce

3. **Check Documentation**: 
   - [User Guide](../user-guide/interactive-chat.md)
   - [Configuration](../getting-started/configuration.md)

## Next Steps

- [CLI Commands](cli-commands.md) - Command reference
- [Configuration](configuration.md) - Configuration options
- [Getting Started](../getting-started/installation.md) - Installation guide
