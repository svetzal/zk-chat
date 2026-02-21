# Plan: Eliminate Knowledge Duplication Between Zettelkasten and Services

## Problem Summary

The `Zettelkasten` class (372 lines) duplicates logic already cleanly extracted into `DocumentService` and `IndexService`. Tools accept `Zettelkasten` in their constructors but never call its methods — they immediately create their own `DocumentService`/`IndexService` instances by reaching into `Zettelkasten`'s internal fields. This means `Zettelkasten` has degraded into an informal service locator whose duplicated methods go unused by the tool layer.

## Strategy

Complete the migration to services in **three phases**, each independently shippable with all tests passing. No speculative work — just removing duplication that already has a cleaner home.

---

## Phase 1 — Change Tools to Accept Services Directly (eliminate service-locator anti-pattern)

### Rationale
Every tool currently takes `Zettelkasten` in its constructor, then immediately pulls out `zk.filesystem_gateway` (or `zk.tokenizer_gateway`, `zk.excerpts_db`, `zk.documents_db`) to construct a service. The tools never call `Zettelkasten` methods. We should inject the services directly.

### Step 1.1: Update `ReadZkDocument` to accept `DocumentService` directly

**File**: `zk_chat/tools/read_zk_document.py`

- Change constructor from `__init__(self, zk: Zettelkasten, ...)` to `__init__(self, document_service: DocumentService, ...)`
- Remove `self.zk = zk` and `self.document_service = DocumentService(zk.filesystem_gateway)`
- Replace with `self.document_service = document_service`
- Remove the `zk: Zettelkasten` class attribute
- Remove the `from zk_chat.zettelkasten import Zettelkasten` import

**File**: `zk_chat/tools/read_zk_document_spec.py`

- Update test fixtures: instead of mocking `Zettelkasten`, create a `Mock(spec=DocumentService)` and pass it directly
- Verify all existing test assertions still pass

### Step 1.2: Update `CreateOrOverwriteZkDocument` to accept `DocumentService` directly

**File**: `zk_chat/tools/create_or_overwrite_zk_document.py`

- Change constructor from `__init__(self, zk: Zettelkasten, ...)` to `__init__(self, document_service: DocumentService, ...)`
- Remove `self.zk = zk` and `self.document_service = DocumentService(zk.filesystem_gateway)`
- Replace with `self.document_service = document_service`
- Remove `Zettelkasten` import

**File**: `zk_chat/tools/create_or_overwrite_zk_document_spec.py`

- Update test fixtures to mock `DocumentService` directly

### Step 1.3: Update `DeleteZkDocument` to accept `DocumentService` directly

**File**: `zk_chat/tools/delete_zk_document.py`

- Same pattern: replace `zk: Zettelkasten` with `document_service: DocumentService`
- Remove `Zettelkasten` import

**File**: `zk_chat/tools/delete_zk_document_spec.py`

- Update test fixtures

### Step 1.4: Update `RenameZkDocument` to accept `DocumentService` directly

**File**: `zk_chat/tools/rename_zk_document.py`

- Same pattern
- Remove `Zettelkasten` import

**File**: `zk_chat/tools/rename_zk_document_spec.py`

- Update test fixtures

### Step 1.5: Update `ListZkDocuments` to accept `DocumentService` directly

**File**: `zk_chat/tools/list_zk_documents.py`

- Same pattern
- Remove `Zettelkasten` import

**File**: `zk_chat/tools/list_zk_documents_spec.py`

- Update test fixtures

### Step 1.6: Update `FindExcerptsRelatedTo` to accept `IndexService` directly

**File**: `zk_chat/tools/find_excerpts_related_to.py`

- Change constructor from `__init__(self, zk: Zettelkasten, ...)` to `__init__(self, index_service: IndexService, ...)`
- Remove `self.zk = zk` and the 4-line `IndexService(...)` construction
- Replace with `self.index_service = index_service`
- Remove `Zettelkasten` import

**File**: `zk_chat/tools/find_excerpts_related_to_spec.py`

- Update test fixtures to mock `IndexService` directly

### Step 1.7: Update `FindZkDocumentsRelatedTo` to accept `IndexService` directly

**File**: `zk_chat/tools/find_zk_documents_related_to.py`

- Same pattern as step 1.6
- Remove `Zettelkasten` import

**File**: `zk_chat/tools/find_zk_documents_related_to_spec.py`

- Update test fixtures

### Step 1.8: Update `FindBacklinks` to accept `LinkTraversalService` and `DocumentService` directly

**File**: `zk_chat/tools/find_backlinks.py`

- Change constructor from `__init__(self, zk: Zettelkasten, ...)` to `__init__(self, link_service: LinkTraversalService, ...)`
- Remove `self.zk = zk` and `self.link_service = LinkTraversalService(zk.filesystem_gateway)`
- Replace with `self.link_service = link_service`
- Note: `FindBacklinks` does NOT use `zk.document_exists()` — it only uses `self.link_service`. So it only needs `LinkTraversalService`.
- Remove `Zettelkasten` import

**File**: `zk_chat/tools/find_backlinks_spec.py`

- Update test fixtures

### Step 1.9: Update `FindForwardLinks` to accept `LinkTraversalService` and `DocumentService` directly

**File**: `zk_chat/tools/find_forward_links.py`

- Change constructor to `__init__(self, link_service: LinkTraversalService, document_service: DocumentService, ...)`
- This tool calls `self.zk.document_exists(source_document)` — so it needs `DocumentService` for the existence check
- Replace `self.zk.document_exists(...)` with `self.document_service.document_exists(...)`
- Remove `Zettelkasten` import

**File**: `zk_chat/tools/find_forward_links_spec.py`

- Update test fixtures

### Step 1.10: Update `AnalyzeImage` to accept `MarkdownFilesystemGateway` directly

**File**: `zk_chat/tools/analyze_image.py`

- Change constructor from `__init__(self, zk: Zettelkasten, llm, ...)` to `__init__(self, filesystem_gateway: MarkdownFilesystemGateway, llm, ...)`
- This tool uses:
  - `self.zk.file_exists(relative_path)` → replace with `self.filesystem_gateway.path_exists(relative_path)`
  - `self.zk.filesystem_gateway.get_absolute_path_for_tool_access(...)` → replace with `self.filesystem_gateway.get_absolute_path_for_tool_access(...)`
- Remove `self.zk` field and `Zettelkasten` import
- Remove the `zk: Zettelkasten` class attribute

**File**: `zk_chat/tools/analyze_image_spec.py`

- Update test fixtures to mock `MarkdownFilesystemGateway` directly

### Step 1.11: Update `ListZkImages` to accept `MarkdownFilesystemGateway` directly

**File**: `zk_chat/tools/list_zk_images.py`

- Change constructor from `__init__(self, zk: Zettelkasten, ...)` to `__init__(self, filesystem_gateway: MarkdownFilesystemGateway, ...)`
- This tool only uses `self.zk.filesystem_gateway.iterate_files_by_extensions(...)` → replace with `self.filesystem_gateway.iterate_files_by_extensions(...)`
- Remove `Zettelkasten` import

**File**: `zk_chat/tools/list_zk_images_spec.py`

- Update test fixtures

### Step 1.12: Update tool wiring in `agent.py`

**File**: `zk_chat/agent.py`

In the `agent()` function:
- After creating `zk`, create services explicitly:
  ```python
  document_service = DocumentService(filesystem_gateway)
  index_service = IndexService(
      tokenizer_gateway=TokenizerGateway(),
      excerpts_db=...,  # same VectorDatabase instances
      documents_db=...,
      filesystem_gateway=filesystem_gateway
  )
  link_service = LinkTraversalService(filesystem_gateway)
  ```
- Update tool instantiations:
  ```python
  ReadZkDocument(document_service),
  ListZkDocuments(document_service),
  ListZkImages(filesystem_gateway),
  FindExcerptsRelatedTo(index_service),
  FindZkDocumentsRelatedTo(index_service),
  CreateOrOverwriteZkDocument(document_service),
  RenameZkDocument(document_service),
  DeleteZkDocument(document_service),
  FindBacklinks(link_service),
  FindForwardLinks(link_service, document_service),
  AnalyzeImage(filesystem_gateway, LLMBroker(...)),
  ```
- Note: `Zettelkasten` is still needed in `agent.py` because `index.py` imports it. But the tools no longer need it.
- Apply the **same changes** to `agent_single_query()` (which has the same duplicated tool wiring — this is another duplication to address, see Phase 2)

### Step 1.13: Update tool wiring in `qt.py`

**File**: `zk_chat/qt.py`

In `MainWindow.initialize_chat_session()`:
- Create services from the same gateways
- Update tool instantiations to match the new constructors (same pattern as agent.py)
- `Zettelkasten` is no longer needed in qt.py if all tools use services

### Step 1.14: Update tool wiring in `mcp.py`

**File**: `zk_chat/mcp.py`

- Change `MCPServer.__init__()` to accept services instead of `Zettelkasten`:
  ```python
  def __init__(self, document_service: DocumentService, index_service: IndexService,
               smart_memory: SmartMemory, enable_unsafe_operations: bool = False)
  ```
- Update `_register_tools()` to pass services to tools
- Update `create_mcp_server()` helper function signature
- Update any callers of `create_mcp_server()`
- Remove `Zettelkasten` import

**File**: `zk_chat/mcp_spec.py` (if exists)

- Update test fixtures

### Step 1.15: Run quality gates

- Run `uv run pytest` — all 217+ tests must pass
- Run `uv run ruff check zk_chat` — zero warnings
- Run `uv run pytest --cov` — coverage should not decrease

---

## Phase 2 — Remove Duplicated Wiring in `agent.py` and Migrate `index.py` / `diagnose.py`

### Rationale
`agent()` and `agent_single_query()` contain near-identical gateway/Zettelkasten/tool construction code. Additionally, `index.py` and `diagnose.py` still use `Zettelkasten` for indexing and querying operations that should go through `IndexService`.

### Step 2.1: Extract shared wiring logic in `agent.py`

**File**: `zk_chat/agent.py`

- Both `agent()` and `agent_single_query()` duplicate ~40 lines of gateway creation, VectorDatabase creation, service creation, and tool wiring
- Extract a helper function (e.g., `_build_tools(config, filesystem_gateway, ...)`) that returns the `tools` list
- Both functions call the helper — eliminating ~40 lines of duplication

### Step 2.2: Migrate `index.py` to use `IndexService` instead of `Zettelkasten`

**File**: `zk_chat/index.py`

- `_build_zk()` creates a `Zettelkasten` — change to `_build_index_service()` creating an `IndexService`
- `_full_reindex()` calls `zk.reindex(...)` → change to `index_service.reindex_all(...)`
- `_incremental_reindex()` calls `zk.update_index(...)` → change to `index_service.update_index(...)`
- Update `reindex()` to use `IndexService`
- Remove `Zettelkasten` import

### Step 2.3: Migrate `diagnose.py` to use services instead of `Zettelkasten`

**File**: `zk_chat/commands/diagnose.py`

- `_run_test_query()` creates a `Zettelkasten` and calls `zk.query_documents()` / `zk.query_excerpts()` → use `IndexService` instead
- Remove `Zettelkasten` import

### Step 2.4: Run quality gates

- Run `uv run pytest` — all tests must pass
- Run `uv run ruff check zk_chat` — zero warnings
- Run `uv run pytest --cov` — coverage should not decrease

---

## Phase 3 — Retire `Zettelkasten` class

### Rationale
After Phases 1-2, no file should import `Zettelkasten` except possibly the service registry. We can now safely remove it.

### Step 3.1: Audit remaining `Zettelkasten` consumers

- Run `grep -r "Zettelkasten" zk_chat/` to find any remaining references
- Expected remaining consumers after Phase 1-2:
  - `zk_chat/zettelkasten.py` (the class itself)
  - `zk_chat/zettelkasten_spec.py` (its tests)
  - `zk_chat/services/service_provider.py` (has `get_zettelkasten()`)
  - `zk_chat/services/service_registry.py` (has `ZETTELKASTEN` enum)

### Step 3.2: Remove `Zettelkasten` from `ServiceProvider` and `ServiceRegistry`

**File**: `zk_chat/services/service_provider.py`

- Remove `get_zettelkasten()` method

**File**: `zk_chat/services/service_registry.py`

- Remove `ZETTELKASTEN` from `ServiceType` enum (only if no other code references it)

### Step 3.3: Delete `Zettelkasten` class and its tests

**Files to delete**:
- `zk_chat/zettelkasten.py`
- `zk_chat/zettelkasten_spec.py`

### Step 3.4: Verify no remaining references

- Run `grep -r "zettelkasten" zk_chat/ --include="*.py"` (case-insensitive) to catch any lingering imports or string references
- Fix any found references

### Step 3.5: Run final quality gates

- Run `uv run pytest` — all tests must pass
- Run `uv run ruff check zk_chat` — zero warnings
- Run `uv run pytest --cov` — coverage should remain stable (we're removing duplicate code and duplicate tests)
- Run `uvx pip-audit` — no new vulnerabilities

---

## Risk Mitigation

- **Each phase ships independently**: Tests pass at every step boundary
- **No behavior changes**: We're only changing how dependencies are wired, not what the tools do
- **Backward compatible within each step**: Each step within a phase can also be committed independently
- **Test coverage preserved**: Tool tests are updated to mock the narrower service interfaces, which is actually better (more focused mocks)

## Expected Outcome

| Metric | Before | After |
|--------|--------|-------|
| `Zettelkasten` lines | 372 | 0 (deleted) |
| Duplicated `_merge_metadata()` | 2 copies | 1 copy (in `DocumentService`) |
| Duplicated CRUD logic | 2 copies | 1 copy (in `DocumentService`) |
| Duplicated indexing logic | 2 copies | 1 copy (in `IndexService`) |
| Tool constructor pattern | `zk: Zettelkasten` → internal service creation | Direct service injection |
| Files importing `Zettelkasten` | 17 | 0 |
| Test count | 217+ | ~200+ (Zettelkasten tests removed, tool tests simplified) |
