# Git Integration

Git integration provides version control for your Zettelkasten when using file modification features.

## Overview

When enabled with the `--git` flag, zk-chat can:
- Initialize a Git repository
- View uncommitted changes
- Commit changes with AI-generated messages
- Provide safety for file modifications

## Enabling Git Integration

```bash
zk-chat interactive --git
```

For file modification support:
```bash
zk-chat interactive --unsafe --git
```

## Features

### Automatic Repository Initialization

If your vault doesn't have a Git repository, zk-chat will create one:

```bash
$ zk-chat interactive --git
Initializing Git repository...
Git repository initialized
```

### View Uncommitted Changes

Ask the AI to show pending changes:

```
You: What files have changed?

AI: Using tool: view_uncommitted_changes

Modified files:
M  Daily Notes/2024-01-15.md
M  Projects/Website Redesign.md

New files:
A  Inbox/New Idea.md

Deleted files:
D  Archive/Old Draft.md
```

### Commit Changes

Let the AI commit changes with generated commit messages:

```
You: Commit these changes

AI: Using tool: commit_changes

Generated commit message:
"Update daily notes and project documentation, add new idea to inbox"

Changes committed successfully.
Commit: a1b2c3d
```

## Why Use Git Integration?

### Safety Net

**Without Git:**
- File modifications are permanent
- No way to undo changes
- No history of what changed

**With Git:**
- Every change is tracked
- Easy to undo mistakes
- Full history available

### Change Tracking

See exactly what the AI modified:

```bash
# View recent changes
git log

# See specific commit
git show <commit-hash>

# View current status
git status
```

### Undo Capability

Revert changes if needed:

```bash
# Undo last commit but keep changes
git reset --soft HEAD~1

# Undo last commit completely
git reset --hard HEAD~1

# Revert specific commit
git revert <commit-hash>
```

## Use Cases

### Content Creation

```bash
zk-chat interactive --unsafe --git --agent

You: Create a summary of all my machine learning notes

AI: [Creates comprehensive summary document]
Using tool: commit_changes
Committed: "Add machine learning notes summary"
```

### Document Updates

```
You: Update my GTD system notes with new insights

AI: [Modifies document]
Using tool: commit_changes  
Committed: "Update GTD system with new workflow insights"
```

### Bulk Changes

```
You: Add tags to all my productivity documents

AI: [Modifies multiple files]
Using tool: commit_changes
Committed: "Add tags to productivity documents"
```

## Best Practices

### Always Use Git with --unsafe

!!! danger "Important"
    Never use `--unsafe` without `--git`. File modifications without version control are risky.

```bash
# Good
zk-chat interactive --unsafe --git

# Bad (no safety net)
zk-chat interactive --unsafe
```

### Review Before Committing

Check what changed:
```bash
git diff
git status
```

### Regular Commits

Commit frequently to create granular history:
- After each significant change
- Before making new modifications
- When switching tasks

### Meaningful Commit Messages

While the AI generates commit messages, you can customize them:

```bash
# View the commit
git log -1

# Amend if needed
git commit --amend -m "Better message"
```

## Integration with Existing Repositories

### Using Existing Git Repo

If your vault already has a Git repository:

```bash
$ zk-chat interactive --git
Using existing Git repository
```

zk-chat will:
- Use the existing repository
- Not reinitialize
- Respect existing configuration

### Working with Remote Repositories

zk-chat doesn't push changes automatically. To sync:

```bash
# After AI commits changes
git push origin main

# Before starting session (get latest)
git pull origin main
```

### Branch Strategy

For advanced workflows:

```bash
# Create a branch for AI changes
git checkout -b ai-changes

# Use zk-chat
zk-chat interactive --unsafe --git

# Review changes
git diff main

# Merge if satisfied
git checkout main
git merge ai-changes
```

## Commands

### Git Status

```
You: Show git status
You: What files have changed?
You: Check uncommitted changes
```

### Commit Changes

```
You: Commit these changes
You: Save my work
You: Create a commit
```

## Troubleshooting

### Git Not Initialized

**Error:** "Git repository not found"

**Solution:**
```bash
# Use --git flag
zk-chat interactive --git
```

### Merge Conflicts

If you manually edit files and the AI tries to modify them:

```bash
# Resolve conflicts manually
git status
# Edit conflicted files
git add .
git commit
```

### Large Repositories

For vaults with large binary files:

```bash
# Add to .gitignore
echo "*.pdf" >> .gitignore
echo "*.mp4" >> .gitignore
git add .gitignore
git commit -m "Ignore large binary files"
```

## Git Configuration

### User Information

Set your Git identity:

```bash
git config user.name "Your Name"
git config user.email "you@example.com"
```

### Ignore Files

Create `.gitignore` in your vault:

```
# zk-chat files (if you want to exclude them)
.zk_chat
.zk_chat_db/

# OS files
.DS_Store
Thumbs.db

# Large files
*.pdf
*.mp4
```

## Advanced Usage

### Pre-commit Hooks

Add validation:

```bash
# .git/hooks/pre-commit
#!/bin/bash
# Run linting or validation
echo "Validating markdown files..."
```

### Git Hooks with zk-chat

Hooks run automatically on commits made by the AI.

### Viewing History

```bash
# All commits
git log

# With file changes
git log --stat

# Graphical view
git log --graph --oneline

# Specific file
git log --follow filename.md
```

## See Also

- [Command Line Interface](../usage/cli.md) - CLI reference
- [Interactive Chat](../usage/interactive-chat.md) - Using git in chat
- [Available Tools](tools.md) - Git tool details
