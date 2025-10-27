# Index Management

The index is a vector database that enables fast semantic search across your Zettelkasten. This guide explains how to manage and optimize your index.

## What is the Index?

The index is a ChromaDB vector database stored in `.zk_chat_db/` in your vault. It contains:

- Embeddings of your document content
- Document metadata
- Vector representations for semantic search

## Index Commands

### Check Index Status

View information about your current index:

```bash
zk-chat index status
```

This displays:

- Number of indexed documents
- Last index update time
- Index location

### Rebuild Index

Update the index with new or modified documents:

```bash
# Incremental rebuild (fast)
zk-chat index rebuild

# Full rebuild (slower, more comprehensive)
zk-chat index rebuild --full
```

## When to Rebuild

### Incremental Rebuild

Use incremental rebuild when:

- You've added new documents
- You've modified existing documents
- Running regular maintenance

```bash
zk-chat index rebuild
```

Incremental rebuilds only process changed files.

### Full Rebuild

Use full rebuild when:

- Index seems corrupted or incomplete
- After major vault reorganization
- Switching embedding models
- Troubleshooting search issues

```bash
zk-chat index rebuild --full
```

Full rebuilds reprocess all documents from scratch.

## Automatic Indexing

### On Chat Start

The first time you use a vault, Zk-Chat performs a full index.

### Force Reindex on Start

Reindex before starting a chat session:

```bash
# Incremental
zk-chat interactive --reindex

# Full
zk-chat interactive --reindex --full
```

## Index Optimization

### Regular Maintenance

For best performance:

```bash
# Weekly incremental rebuild
zk-chat index rebuild
```

Add to a cron job or scheduled task for automatic maintenance.

### After Bulk Changes

After importing many documents or major reorganization:

```bash
zk-chat index rebuild --full
```

## Index Location

The index is stored in your vault:

```
your-vault/
├── .zk_chat           # Configuration
├── .zk_chat_db/       # Index database
│   └── ...            # ChromaDB files
└── your-documents...
```

### Excluding from Version Control

Add to `.gitignore`:

```gitignore
.zk_chat_db/
```

The index can be rebuilt from your documents, so it doesn't need to be versioned.

## Troubleshooting

### Index Build Fails

1. Check available disk space
2. Verify vault path is correct
3. Ensure documents are readable
4. Try full rebuild: `zk-chat index rebuild --full`

### Search Not Finding Documents

1. Rebuild index: `zk-chat index rebuild`
2. Check document is in markdown format
3. Verify document is in vault directory
4. Try full rebuild if issues persist

### Index Corruption

If you suspect corruption:

```bash
# Delete index and rebuild
rm -rf /path/to/vault/.zk_chat_db
zk-chat index rebuild --full
```

### Performance Issues

For large vaults:

- Use incremental rebuilds for regular updates
- Schedule full rebuilds during off-hours
- Ensure adequate system resources

## Next Steps

- [Smart Memory](smart-memory.md) - Persistent context storage
- [MCP Servers](mcp-servers.md) - External tool integration
- [Troubleshooting Guide](../reference/troubleshooting.md) - Common issues
