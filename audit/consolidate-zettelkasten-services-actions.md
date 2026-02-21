All quality gates pass. Here's what was accomplished:

---

## Refactoring Complete

**All three phases executed successfully.**

### Results
- ✅ **211 tests pass** (217 before — the 6-test reduction is the deleted `zettelkasten_spec.py`)
- ✅ **Zero ruff warnings**
- ✅ **Zero remaining `Zettelkasten` class imports** in the codebase

---

### What Changed

**Phase 1 — Tools now accept focused services directly** (21 files):
| Tool | Before | After |
|---|---|---|
| `ReadZkDocument`, `CreateOrOverwriteZkDocument`, `DeleteZkDocument`, `RenameZkDocument`, `ListZkDocuments` | `Zettelkasten` → extracted `DocumentService` | `DocumentService` directly |
| `FindExcerptsRelatedTo`, `FindZkDocumentsRelatedTo` | `Zettelkasten` → extracted `IndexService` | `IndexService` directly |
| `FindBacklinks` | `Zettelkasten` → extracted `LinkTraversalService` | `LinkTraversalService` directly |
| `FindForwardLinks` | `Zettelkasten` → extracted both services | `DocumentService` + `LinkTraversalService` |
| `AnalyzeImage`, `ListZkImages` | `Zettelkasten.filesystem_gateway` | `MarkdownFilesystemGateway` directly |

**Phase 1 — Wiring extracted** (3 files):
- `agent.py`: duplicate tool-building code collapsed into a single `_build_tools()` helper; both `agent()` and `agent_single_query()` call it
- `mcp.py`: `MCPServer` now accepts `DocumentService` + `IndexService` instead of `Zettelkasten`
- `qt.py`: `initialize_chat_session()` constructs services directly

**Phase 2 — Remaining callers migrated** (2 files):
- `index.py`: `_build_zk()` → `_build_index_service()`, `zk.reindex()` → `index_service.reindex_all()`
- `commands/diagnose.py`: `Zettelkasten(...)` → `IndexService(...)`, queries go through service

**Phase 3 — Zettelkasten retired** (5 files):
- `zettelkasten.py` — deleted (372 lines of duplicate logic)
- `zettelkasten_spec.py` — deleted
- `service_provider.py` — removed `get_zettelkasten()`
- `service_registry.py` — removed `ZETTELKASTEN` enum value
- `plugin_base.py` — replaced `zettelkasten` property with `document_service`, `index_service`, and `link_traversal_service` properties