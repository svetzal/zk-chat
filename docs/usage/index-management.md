# Index Management

zk-chat creates a vector database index of your documents for fast semantic search.

## Understanding the Index

The index is stored in `.zk_chat_db/` in your vault and contains:

- Vector embeddings of your documents
- Document metadata (paths, titles, modified times)
- Chunk mappings for efficient retrieval

## Checking Index Status

```bash
zk-chat index status
```

This shows:
- Number of indexed documents
- Last update time
- Index location
- Index size

## Rebuilding the Index

### Incremental Rebuild (Fast)

```bash
zk-chat index rebuild
```

This:
- Scans for new or modified documents
- Updates only what's changed
- Typically completes in seconds

**When to use:**
- After adding a few new documents
- After editing existing documents
- Regular maintenance

### Full Rebuild (Comprehensive)

```bash
zk-chat index rebuild --full
```

This:
- Deletes the existing index
- Re-indexes all documents from scratch
- May take several minutes for large vaults

**When to use:**
- After major vault reorganization
- If search results seem incorrect
- After upgrading zk-chat versions
- When troubleshooting index issues

## Automatic Reindexing

You can rebuild the index when starting a chat session:

```bash
# Incremental rebuild
zk-chat interactive --reindex

# Full rebuild
zk-chat interactive --reindex --full
```

## When to Rebuild

### Rebuild Needed

- ✅ After adding new documents
- ✅ After editing document content
- ✅ After renaming or moving files
- ✅ If search doesn't find expected results

### Full Rebuild Needed

- ⚠️ After vault structure changes
- ⚠️ After upgrading zk-chat
- ⚠️ If index appears corrupted
- ⚠️ After changing embedding models

### Rebuild Not Needed

- ❌ Before every query
- ❌ After just reading documents
- ❌ Between chat sessions

## Index Performance

### Indexing Speed

Factors affecting speed:
- **Vault size**: Larger vaults take longer
- **Document complexity**: Long documents take more time
- **Model used**: Embedding generation varies by model
- **System resources**: CPU/GPU availability matters

Typical speeds:
- Small vault (< 100 docs): < 30 seconds
- Medium vault (100-1000 docs): 1-5 minutes
- Large vault (> 1000 docs): 5-15 minutes

### Search Speed

Once indexed, searches are fast:
- Typical query: < 1 second
- Complex queries: 1-3 seconds

## Index Maintenance

### Regular Maintenance

Good practice:
```bash
# Weekly or after significant changes
zk-chat index rebuild
```

### Deep Cleaning

Occasionally:
```bash
# Monthly or after major updates
zk-chat index rebuild --full
```

## Troubleshooting

### Index Appears Corrupted

**Symptoms:**
- Search returns no results
- Error messages about index
- Crashes during search

**Solution:**
```bash
zk-chat index rebuild --full
```

### Index Too Large

**Symptom:** `.zk_chat_db/` folder is very large

**Causes:**
- Many documents
- Long documents
- Multiple rebuilds without cleaning

**Solution:**
```bash
# Full rebuild cleans up old data
zk-chat index rebuild --full
```

### Slow Indexing

**Causes:**
- Large vault
- Slow disk
- Resource constraints

**Solutions:**
- Close other applications
- Use faster storage (SSD)
- Index during off-hours
- Consider a smaller embedding model

### New Documents Not Found

**Problem:** Recently added documents don't appear in searches

**Solution:**
```bash
zk-chat index rebuild
```

The index doesn't update automatically; you need to rebuild it.

## Index Storage Location

The index is stored in your vault:

```
your-vault/
├── .zk_chat_db/           # Index database
│   ├── chroma.sqlite3     # Vector database
│   └── ...
├── .zk_chat               # Configuration
└── your-documents.md
```

### Moving Your Vault

If you move your vault, the index moves with it. No rebuild needed unless paths change internally.

### Multiple Vaults

Each vault has its own index. They don't interfere with each other.

## Technical Details

### Embedding Model

By default, zk-chat uses the embedding model provided by your chosen gateway:
- **Ollama**: Uses the model's built-in embeddings
- **OpenAI**: Uses OpenAI's embedding API

### Chunk Size

Documents are split into chunks for embedding:
- Default chunk size: optimized for the model
- Overlapping chunks ensure context preservation
- Chunk metadata enables precise retrieval

### Vector Dimensions

Embedding dimensions depend on the model:
- Different models = different dimensions
- Changing models requires full rebuild
- Higher dimensions = more detailed but slower

## Best Practices

1. **Rebuild Regularly**: After significant vault changes
2. **Use Incremental**: Default rebuild is usually sufficient
3. **Full Rebuild Sparingly**: Only when needed
4. **Monitor Index Size**: Keep an eye on `.zk_chat_db/` size
5. **Clean Rebuilds**: Use `--full` after major updates

## See Also

- [Command Line Interface](cli.md) - CLI reference
- [Configuration](../configuration/advanced.md) - Advanced settings
