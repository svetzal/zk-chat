# Vault Setup

Configuring your Zettelkasten vault for use with zk-chat.

## What is a Vault?

A vault is your Zettelkasten - a folder containing your markdown notes and documents. Common tools that create vaults:

- **Obsidian** - Popular note-taking app
- **Logseq** - Outliner-based knowledge base
- **Foam** - VS Code extension
- **Any markdown editor** - Plain text files

## Requirements

Your vault should contain:
- Markdown files (`.md`)
- UTF-8 text encoding
- Accessible file system location

## Setting Your Vault Path

### On First Run

```bash
zk-chat interactive --vault /path/to/your/vault
```

### Bookmarking Vaults

Save frequently used vaults:

```bash
# Save current vault
zk-chat interactive --vault /path/to/vault --save

# List bookmarks
zk-chat interactive --list-bookmarks

# Remove bookmark
zk-chat interactive --remove-bookmark /path/to/vault
```

After bookmarking, you can omit `--vault`:

```bash
# Uses last/bookmarked vault
zk-chat interactive
```

## Multiple Vaults

You can work with multiple vaults:

```bash
# Work vault
zk-chat interactive --vault ~/Documents/Work

# Personal vault  
zk-chat interactive --vault ~/Documents/Personal

# Each vault maintains its own:
# - Configuration (.zk_chat)
# - Index (.zk_chat_db/)
# - System prompt (ZkSystemPrompt.md)
```

## Vault Structure

### Recommended Organization

```
your-vault/
├── Daily Notes/
│   ├── 2024-01-15.md
│   └── 2024-01-16.md
├── Projects/
│   ├── Project A.md
│   └── Project B.md
├── Reference/
│   ├── Books.md
│   └── Articles.md
├── Templates/
│   └── Daily Template.md
├── .zk_chat              # zk-chat config
├── .zk_chat_db/          # Vector database
└── ZkSystemPrompt.md     # System prompt
```

### zk-chat Files

zk-chat creates these files in your vault:

**`.zk_chat`** - Configuration file
```yaml
vault: /path/to/vault
model: qwen2.5:14b
gateway: ollama
visual_model: llava
```

**`.zk_chat_db/`** - Vector database
- Contains ChromaDB files
- Can be safely deleted to rebuild
- Managed automatically

**`ZkSystemPrompt.md`** - System prompt (optional)
- Defines AI behavior
- Customizable
- Created automatically if `--store-prompt` is used

## Vault Best Practices

### File Organization

**Use descriptive names:**
```
✅ Getting Things Done System.md
❌ gtd.md
```

**Organize by topic:**
```
productivity/
├── GTD System.md
├── Time Management.md
└── Focus Techniques.md
```

**Use consistent structure:**
- Keep similar content together
- Create index/MOC (Map of Content) files
- Use folders sparingly (flat is often better)

### Wikilinks

Use wikilinks to connect ideas:

```markdown
The [[Getting Things Done]] system uses [[Context Lists]] 
to organize [[Next Actions]].
```

**Tips:**
- Link related concepts
- Use consistent naming
- Create bidirectional links
- Build hub documents

### Frontmatter (Optional)

Add metadata to documents:

```markdown
---
title: Getting Things Done
tags: [productivity, gtd, workflow]
created: 2024-01-15
---

# Getting Things Done

Content here...
```

## Git Integration

### Existing Git Repository

If your vault already uses Git:

```bash
# zk-chat will use existing repo
zk-chat interactive --git
```

### New Git Repository

zk-chat can initialize Git:

```bash
# Initializes Git if needed
zk-chat interactive --git --unsafe
```

### .gitignore

Optionally exclude zk-chat files:

```gitignore
# .gitignore

# Exclude zk-chat (if desired)
.zk_chat
.zk_chat_db/

# But keep system prompt (if customized)
!ZkSystemPrompt.md
```

## System Prompt

### What is the System Prompt?

The system prompt defines how the AI behaves when working with your vault. It's stored in `ZkSystemPrompt.md`.

### Default Behavior

By default, zk-chat creates and uses `ZkSystemPrompt.md`.

### Customizing

Edit `ZkSystemPrompt.md` to change AI behavior:

```markdown
You are an AI assistant specialized in helping with my Zettelkasten.

Focus on:
- Providing detailed technical explanations
- Using examples from software development
- Connecting ideas across documents

Always:
- Cite specific documents
- Suggest related notes
- Use precise wikilink syntax
```

### Disabling

Don't create/use the system prompt file:

```bash
zk-chat interactive --no-store-prompt
```

## Vault Backup

### Why Backup?

Protect your knowledge base from:
- Accidental deletions
- File corruption
- System failures

### Backup Strategies

**Git (Recommended):**
```bash
# Use Git for version control
git init
git add .
git commit -m "Initial commit"

# Push to remote
git remote add origin https://github.com/user/vault.git
git push -u origin main
```

**Cloud Sync:**
- Obsidian Sync
- Syncthing
- iCloud Drive
- Dropbox
- Google Drive

**Local Backup:**
```bash
# Time Machine (Mac)
# Windows Backup
# rsync script
rsync -av --delete ~/vault/ ~/backup/vault/
```

## Common Vault Patterns

### Obsidian Vault

```
vault/
├── Daily Notes/
├── Templates/
├── Attachments/
│   └── images/
├── .obsidian/        # Obsidian config (ignored by zk-chat)
├── .zk_chat          # zk-chat config
└── notes...
```

### Logseq Vault

```
vault/
├── journals/
├── pages/
├── assets/
├── logseq/           # Logseq config (ignored by zk-chat)
├── .zk_chat          # zk-chat config
└── notes...
```

### Plain Markdown

```
vault/
├── index.md
├── topics/
├── references/
├── .zk_chat
└── notes...
```

## Troubleshooting

### Vault Not Found

**Error:** "Vault not found at path"

**Check:**
- Path is correct
- Path is absolute
- Directory exists
- Has read permissions

### Can't Write to Vault

**Error:** Permission denied

**Solutions:**
```bash
# Check permissions
ls -la /path/to/vault

# Fix permissions
chmod u+w /path/to/vault
```

### Large Vault Performance

For vaults with thousands of files:

```bash
# Use incremental rebuilds
zk-chat index rebuild

# Only full rebuild when necessary
zk-chat index rebuild --full
```

## See Also

- [Installation](../installation.md) - Initial setup
- [Model Selection](models.md) - Choosing models
- [Index Management](../usage/index-management.md) - Managing the index
- [Git Integration](../features/git-integration.md) - Version control
