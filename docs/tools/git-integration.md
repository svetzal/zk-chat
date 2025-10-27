# Git Integration Tools

Zk-Chat includes Git integration tools to help manage version control for your Zettelkasten.

## Setup

Enable Git integration with the `--git` flag:

```bash
zk-chat interactive --git
```

If your vault doesn't have a Git repository, Zk-Chat will initialize one automatically.

## Why Use Git with Zk-Chat?

Git integration provides:

- **Version history** for all changes
- **Ability to revert** unwanted modifications
- **Change tracking** for AI-generated content
- **Backup** of your knowledge base

!!! tip "Strongly Recommended with Unsafe Mode"
    Always use `--git` when enabling `--unsafe` mode to protect against unintended changes.

## Available Tools

### View Uncommitted Changes

Shows pending changes in your Zettelkasten vault.

**Use cases:**

- Reviewing AI-generated changes
- Checking what's been modified
- Deciding what to commit

**Example:**

```
You: What changes have been made?
AI: [Shows git diff of uncommitted changes]
```

### Commit Changes

Commits changes with AI-generated commit messages.

**Requires:** `--git` flag

**Use cases:**

- Saving changes to version history
- Creating checkpoints
- Organizing work sessions

**Example:**

```
You: Commit these changes
AI: [Generates a descriptive commit message and commits the changes]
```

The AI will:

1. Review the changes
2. Generate an appropriate commit message
3. Commit the changes

## Workflow Examples

### Safe Editing Workflow

```bash
# Start with git enabled
zk-chat interactive --unsafe --git
```

```
You: Create a summary of my project notes
AI: [Creates the summary document]

You: What changes were made?
AI: [Shows git diff - new file created]

You: Commit these changes
AI: [Commits with message like "Add project notes summary"]
```

### Review and Revert

```
You: Update all project documents with new status
AI: [Updates multiple documents]

You: Show me what changed
AI: [Shows all changes using git diff]

You: Actually, revert those changes
AI: [Uses git to revert the changes]
```

### Session Checkpoints

```
You: Commit my changes so far
AI: [Commits current work]

You: [Continue working]

You: Commit again
AI: [Commits new changes with different message]
```

## Manual Git Operations

You can also use Git commands directly:

```bash
# View status
cd /path/to/vault
git status

# View changes
git diff

# View history
git log

# Revert to previous commit
git reset --hard HEAD~1
```

## AI-Generated Commit Messages

The AI generates commit messages based on:

- Files changed
- Type of changes (new, modified, deleted)
- Content of changes

**Example messages:**

- "Add machine learning summary document"
- "Update project status in 3 documents"
- "Reorganize research notes structure"

## Best Practices

### Commit Often

Create commits at logical checkpoints:

```
You: Commit this summary
AI: [Commits the summary]

You: [Continue working]

You: Commit the reorganization
AI: [Commits the reorganization separately]
```

### Review Before Committing

Always review changes first:

```
You: What changes have been made?
AI: [Shows changes]

You: [Review the changes]

You: Commit these changes
AI: [Commits after review]
```

### Use Descriptive Requests

Help the AI generate better commit messages:

```
You: Commit these changes to the project structure
AI: [Generates message like "Reorganize project structure"]
```

Instead of:

```
You: Commit
AI: [Generates generic message like "Update files"]
```

### Keep Index Separate

Add `.zk_chat_db/` to `.gitignore`:

```gitignore
# Zk-Chat database (can be rebuilt)
.zk_chat_db/
```

The index can be rebuilt, so it doesn't need to be in version control.

## Git Configuration

### Initialize Manually

If you prefer to initialize Git yourself:

```bash
cd /path/to/vault
git init
git add .
git commit -m "Initial commit"
```

Then use Zk-Chat with `--git`.

### Existing Repository

Zk-Chat works with existing Git repositories. Just use `--git`:

```bash
zk-chat interactive --git
```

### Remote Repositories

To push to remote repositories:

```bash
# Set up remote
cd /path/to/vault
git remote add origin https://github.com/username/vault.git

# Push changes
git push -u origin main
```

Zk-Chat doesn't push automatically - you control when to sync with remotes.

## Troubleshooting

### Git Not Working

Ensure Git is installed:

```bash
git --version
```

### Uncommitted Changes Warning

If you have uncommitted changes:

1. Review them: "What changes have been made?"
2. Commit them: "Commit these changes"
3. Or revert them manually: `git reset --hard`

### Merge Conflicts

Zk-Chat doesn't handle merge conflicts. Resolve them manually:

```bash
cd /path/to/vault
git status
# Edit conflicted files
git add .
git commit -m "Resolve conflicts"
```

## Advanced Usage

### Branching

Create branches for experimental work:

```bash
cd /path/to/vault
git checkout -b experiment
```

Use Zk-Chat on the branch:

```bash
zk-chat interactive --git
```

Merge when satisfied:

```bash
git checkout main
git merge experiment
```

### Cherry-Picking

Apply specific commits:

```bash
git cherry-pick <commit-hash>
```

### History Review

Review commit history:

```bash
git log --oneline
git show <commit-hash>
```

## Next Steps

- [Document Management](document-management.md) - Working with documents
- [Configuration](../getting-started/configuration.md) - Configure Git options
- [Interactive Chat](../user-guide/interactive-chat.md) - Using Git tools in chat
