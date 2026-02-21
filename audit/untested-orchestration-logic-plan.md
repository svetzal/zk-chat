---

## Step-by-Step Plan: Closing the Testing Gaps in zk-chat

### Step 0: Make Coverage Honest

**File to modify:** `pyproject.toml`

Add a `[tool.pytest.ini_options]` coverage source configuration so that all source files under `zk_chat/` are measured even when no test imports them:

```toml
[tool.coverage.run]
source = ["zk_chat"]

[tool.coverage.report]
show_missing = true
fail_under = 92
```

This ensures `uv run pytest --cov` measures every `.py` file in `zk_chat/`, not just those transitively imported by spec files. After adding this, run `uv run pytest --cov` to establish the true baseline coverage number before proceeding.

---

### Step 1: Test `strip_thinking()` — Pure Function Quick Win

**New file:** `zk_chat/iterative_problem_solving_agent_spec.py`

This is the lowest-hanging fruit in the entire codebase: a pure function with zero dependencies.

Write a `DescribeStripThinking` test class with the following test cases:

1. **`should_return_text_unchanged_when_no_think_tags_present`** — Input: `"Hello world"` → Output: `"Hello world"`
2. **`should_remove_single_think_block`** — Input: `"before <think>internal</think> after"` → Output: `"before  after"` (stripped)
3. **`should_remove_multiple_think_blocks`** — Input: `"a <think>x</think> b <think>y</think> c"` → verify both blocks removed
4. **`should_handle_multiline_content_inside_think_tags`** — Input with `\n` inside `<think>...</think>` → verify removal (tests the `re.DOTALL` flag)
5. **`should_strip_leading_and_trailing_whitespace_from_result`** — Input: `"  <think>stuff</think>  text  "` → Output: `"text"`
6. **`should_return_empty_string_when_input_is_only_think_block`** — Input: `"<think>everything</think>"` → Output: `""`

No mocks needed. No fixtures needed. Pure input/output assertions.

**Verification:** `uv run pytest zk_chat/iterative_problem_solving_agent_spec.py -v`

---

### Step 2: Test `ResolveWikiLink` — Gateway Delegation

**New file:** `zk_chat/tools/resolve_wikilink_spec.py`

This tool wraps `MarkdownFilesystemGateway.resolve_wikilink()` with success/error branching.

**Fixtures:**
- `mock_fs` — `Mock(spec=MarkdownFilesystemGateway)`
- `mock_console` — `Mock(spec=RichConsoleService)`
- `tool` — `ResolveWikiLink(mock_fs, mock_console)`

Write a `DescribeResolveWikiLink` test class:

1. **`should_return_relative_path_when_wikilink_resolves_successfully`** — Set `mock_fs.resolve_wikilink.return_value = "notes/my-note.md"`, call `tool.run(wikilink="My Note")`, assert result == `"relative_path: notes/my-note.md"`
2. **`should_return_not_found_message_when_wikilink_raises_value_error`** — Set `mock_fs.resolve_wikilink.side_effect = ValueError("not found")`, call `tool.run(wikilink="Missing")`, assert result == `"There is no document currently present matching the wikilink provided."`
3. **`should_have_descriptor_with_correct_tool_name`** — Assert `tool.descriptor["function"]["name"] == "resolve_wikilink"`
4. **`should_pass_wikilink_parameter_to_filesystem_gateway`** — Call `tool.run(wikilink="Test Link")`, assert `mock_fs.resolve_wikilink.assert_called_once_with("Test Link")`

**Verification:** `uv run pytest zk_chat/tools/resolve_wikilink_spec.py -v`

---

### Step 3: Test `VectorDatabase` — Query Transformation Logic

**New file:** `zk_chat/vector_database_spec.py`

This is where real mapping logic lives: the Chroma nested-list response format is unpacked into `QueryResult` objects.

**Fixtures:**
- `mock_chroma_gateway` — `Mock(spec=ChromaGateway)`
- `mock_llm_gateway` — `Mock(spec=OllamaGateway)` (or whichever LLM gateway is used for embeddings)
- `vector_db` — `VectorDatabase(mock_chroma_gateway, mock_llm_gateway, ZkCollectionName.DOCUMENTS)` (or whatever the collection enum is)

Write a `DescribeVectorDatabase` test class with nested describe classes:

**`class DescribeQuery:`**

1. **`should_return_query_results_from_chroma_response`** — Set up `mock_llm_gateway.calculate_embeddings.return_value = [0.1, 0.2]` and `mock_chroma_gateway.query.return_value = {"ids": [["id1", "id2"]], "documents": [["doc1", "doc2"]], "metadatas": [[{"source": "a"}, {"source": "b"}]], "distances": [[0.1, 0.5]]}`. Call `vector_db.query("test query", n_results=2)`. Assert the returned list has 2 `QueryResult` objects with correct ids, documents, metadata, and distances.
2. **`should_return_empty_list_when_chroma_returns_no_results`** — Set up Chroma response with empty nested lists: `{"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}`. Assert `vector_db.query(...)` returns `[]`.
3. **`should_pass_query_embedding_to_chroma_gateway`** — Verify `mock_chroma_gateway.query` was called with the embedding returned by `mock_llm_gateway.calculate_embeddings`.
4. **`should_forward_n_results_to_chroma_gateway`** — Call with `n_results=5`, verify `mock_chroma_gateway.query` was called with `n_results=5`.

**`class DescribeAddDocuments:`**

5. **`should_calculate_embeddings_for_each_document`** — Pass 2 `VectorDocumentForStorage` objects, verify `mock_llm_gateway.calculate_embeddings` was called twice (once per document).
6. **`should_pass_document_data_and_embeddings_to_chroma_gateway`** — Verify `mock_chroma_gateway.add_items` was called with correct ids, documents, metadatas, and embeddings lists.
7. **`should_handle_empty_document_list`** — Pass empty list, verify `mock_chroma_gateway.add_items` is called with all-empty lists.

**`class DescribeReset:`**

8. **`should_delegate_to_chroma_gateway_with_correct_collection_name`** — Call `vector_db.reset()`, assert `mock_chroma_gateway.reset_indexes` was called with the correct collection name.

**Verification:** `uv run pytest zk_chat/vector_database_spec.py -v`

---

### Step 4: Test `IterativeProblemSolvingAgent.solve()` — Orchestration Logic

**File:** `zk_chat/iterative_problem_solving_agent_spec.py` (append to file created in Step 1)

The `solve()` method has three exit conditions and a final summarization call. We need to mock `ChatSession` since it's the boundary.

**Approach:** The `IterativeProblemSolvingAgent.__init__` creates a `ChatSession` internally. We need to either:
- (a) Patch `ChatSession` at the module level using `unittest.mock.patch`, or
- (b) Refactor the constructor to accept a `ChatSession` (preferred, but more invasive).

**Recommended approach:** Use `unittest.mock.patch` on `mojentic.llm.ChatSession` within the test module. This is acceptable because `ChatSession` is the boundary object (the agent's gateway to LLM). Create a `mock_llm_broker` fixture with `Mock(spec=LLMBroker)`.

Write a `DescribeIterativeProblemSolvingAgent` test class:

**`class DescribeSolve:`**

1. **`should_stop_when_step_result_contains_done`** — Patch `ChatSession` so `send()` returns `"The answer is DONE"` on first call, then returns `"Summary"` on second call (the summarization). Assert the method returns the summary and `send` was called exactly twice.
2. **`should_stop_when_step_result_contains_fail`** — Patch so `send()` returns `"This is a FAIL case"` on first call. Verify early exit and summarization.
3. **`should_stop_after_max_iterations_exhausted`** — Construct agent with `max_iterations=2`. Patch so `send()` returns `"still working..."` for the first two calls (neither DONE nor FAIL), then `"Summary"` for the third. Assert `send` was called 3 times (2 iterations + 1 summary).
4. **`should_detect_done_case_insensitively`** — Patch so `send()` returns `"done"` (lowercase). Verify it still triggers the DONE exit.
5. **`should_detect_fail_case_insensitively`** — Patch so `send()` returns `"fail"` (lowercase). Verify it still triggers the FAIL exit.
6. **`should_strip_thinking_tags_before_checking_exit_conditions`** — Patch so `send()` returns `"<think>internal reasoning</think> DONE"`. Verify the DONE exit is still detected after stripping.
7. **`should_always_send_summarization_prompt_after_loop`** — For each exit condition (DONE, FAIL, max iterations), verify the final `send()` call is always made.
8. **`should_default_max_iterations_to_3`** — Construct without specifying `max_iterations`, patch so `send()` never returns DONE/FAIL. Assert 4 calls to `send` (3 iterations + 1 summary).

**Verification:** `uv run pytest zk_chat/iterative_problem_solving_agent_spec.py -v`

---

### Step 5: Test `MCPServer` — Request Routing and Error Handling

**New file:** `zk_chat/mcp_spec.py`

**Fixtures:**
- `mock_document_service` — `Mock(spec=DocumentService)`
- `mock_index_service` — `Mock(spec=IndexService)`
- `mock_smart_memory` — `Mock(spec=SmartMemory)`
- `server` — `MCPServer(mock_document_service, mock_index_service, mock_smart_memory, enable_unsafe_operations=False)`
- `unsafe_server` — Same but with `enable_unsafe_operations=True`

Write a `DescribeMCPServer` test class with nested describe classes:

**`class DescribeRegisterTools:`**

1. **`should_register_read_only_tools_by_default`** — Assert `server.tools` contains keys for `read_zk_document`, `find_excerpts_related_to`, `find_zk_documents_related_to`, `retrieve_from_smart_memory`, `store_in_smart_memory` (verify exact tool name keys from the descriptors).
2. **`should_not_register_write_tool_when_unsafe_operations_disabled`** — Assert `"create_or_overwrite_zk_document"` (or whatever the key is) NOT in `server.tools`.
3. **`should_register_write_tool_when_unsafe_operations_enabled`** — Assert the write tool key IS in `unsafe_server.tools`.

**`class DescribeExecuteTool:`**

4. **`should_return_success_with_result_when_tool_executes`** — Manually register a mock tool in `server.tools`, set `mock_tool.run.return_value = "result"`. Call `server.execute_tool("mock_tool", {})`. Assert `{"status": "success", "result": "result"}`.
5. **`should_return_error_when_tool_not_found`** — Call `server.execute_tool("nonexistent", {})`. Assert `{"status": "error"}` with appropriate message.
6. **`should_return_error_when_tool_raises_exception`** — Register mock tool that raises `RuntimeError("boom")`. Assert `{"status": "error", "error": "boom"}`.

**`class DescribeProcessRequest:`**

7. **`should_return_error_when_type_key_missing`** — Call with `{}`. Assert error response.
8. **`should_route_tool_call_to_execute_tool`** — Call with `{"type": "tool_call", "tool": "<registered_tool>", "parameters": {}}`. Assert success.
9. **`should_return_error_for_tool_call_missing_tool_key`** — Call with `{"type": "tool_call", "parameters": {}}`. Assert error.
10. **`should_return_error_for_tool_call_missing_parameters_key`** — Call with `{"type": "tool_call", "tool": "x"}`. Assert error.
11. **`should_return_tool_list_for_list_tools_request`** — Call with `{"type": "list_tools"}`. Assert `{"status": "success", "tools": [...]}`.
12. **`should_return_error_for_unsupported_type`** — Call with `{"type": "unknown"}`. Assert error.

**`class DescribeHandleMcpRequest:`**

13. **`should_parse_valid_json_and_delegate_to_process_request`** — Pass a valid JSON string for `list_tools`. Assert success JSON string returned.
14. **`should_return_error_json_for_invalid_json_input`** — Pass `"not valid json"`. Assert returned JSON string contains `"Invalid JSON"`.

**Verification:** `uv run pytest zk_chat/mcp_spec.py -v`

---

### Step 6: Test `index.py` — Extract and Test Orchestration Decisions

**New file:** `zk_chat/index_spec.py`

The `reindex()` function internally constructs a `ServiceProvider`, making it hard to test as-is. Rather than refactoring the production code in this testing pass (which would be a separate task), we test what we can:

**Option A (Preferred — Minimal Refactoring):** Refactor `reindex()` to accept an optional `service_provider` parameter (defaulting to building one internally). This is a one-line change to the function signature and an `if service_provider is None:` guard. This makes the orchestration testable without changing calling code.

**If Option A is approved, proceed with these tests:**

**Fixtures:**
- `mock_index_service` — `Mock(spec=IndexService)`
- `mock_service_provider` — `Mock(spec=ServiceProvider)` configured to return `mock_index_service`
- `mock_config_gateway` — `Mock(spec=ConfigGateway)`
- `mock_config` — A `Config` instance (or `Mock(spec=Config)`) with `last_indexed` attribute

**`class DescribeReindex:`**

1. **`should_use_full_reindex_when_force_full_is_true`** — Call `reindex(config, force_full=True, config_gateway=mock_config_gateway, service_provider=mock_service_provider)`. Assert `mock_index_service.reindex_all` was called (not `update_index`).
2. **`should_use_full_reindex_when_last_indexed_is_none`** — Set `mock_config.last_indexed = None`, call with `force_full=False`. Assert `reindex_all` was called.
3. **`should_use_incremental_reindex_when_last_indexed_is_set_and_not_forced`** — Set `mock_config.last_indexed = datetime(2024, 1, 1)`, call with `force_full=False`. Assert `update_index` was called with `since=` parameter.
4. **`should_save_config_after_indexing`** — Call reindex. Assert `mock_config_gateway.save` was called with the config.
5. **`should_update_last_indexed_timestamp_after_indexing`** — Call reindex. Assert `mock_config.set_last_indexed` was called.

**`class DescribeFullReindex:`** (testing the `_full_reindex` private helper — since it's module-level, we can import it directly as `from zk_chat.index import _full_reindex`)

6. **`should_call_reindex_all_on_index_service`** — Mock the index service and progress tracker. Call `_full_reindex(config, mock_index_service, mock_progress)`. Assert `mock_index_service.reindex_all` was called.

**`class DescribeIncrementalReindex:`**

7. **`should_call_update_index_with_since_parameter`** — Mock index service and progress tracker. Call `_incremental_reindex(config, mock_index_service, mock_progress, last_indexed)`. Assert `mock_index_service.update_index` was called with `since=last_indexed`.

**Verification:** `uv run pytest zk_chat/index_spec.py -v`

---

### Step 7: Run Full Quality Gate

After all spec files are written and passing individually:

1. **Run all tests with coverage:**
   ```bash
   uv run pytest --cov=zk_chat --cov-report=term-missing
   ```
   Verify the coverage number has increased from the baseline established in Step 0. The previously-invisible modules should now show measured coverage.

2. **Run linting with zero warnings:**
   ```bash
   uv run ruff check zk_chat
   ```
   Fix any warnings introduced by new spec files (unused imports, line length, etc.).

3. **Run formatting:**
   ```bash
   uv run ruff format zk_chat
   ```

4. **Run security audit:**
   ```bash
   uvx pip-audit
   ```

---

### Step 8: Update Coverage Threshold

After confirming the new coverage number, update the `fail_under` value in `pyproject.toml` `[tool.coverage.report]` to lock in the new minimum. This prevents future regressions.

---

### Summary of Deliverables

| Step | New/Modified File | Tests Added | Key Behavior Verified |
|------|------------------|-------------|----------------------|
| 0 | `pyproject.toml` | 0 | Honest coverage measurement |
| 1 | `iterative_problem_solving_agent_spec.py` | ~6 | `strip_thinking()` pure function |
| 2 | `tools/resolve_wikilink_spec.py` | ~4 | Wikilink resolution success/error paths |
| 3 | `vector_database_spec.py` | ~8 | Chroma response transformation, embedding delegation |
| 4 | `iterative_problem_solving_agent_spec.py` | ~8 | DONE/FAIL/max-iterations exit conditions |
| 5 | `mcp_spec.py` | ~14 | Tool registration gating, request routing, error handling |
| 6 | `index_spec.py` + minor `index.py` refactor | ~7 | Full vs incremental reindex branching, config persistence |
| 7 | — | 0 | Full quality gate verification |
| 8 | `pyproject.toml` | 0 | Lock in new coverage floor |

**Total: ~47 new tests across 5 new spec files**, targeting the exact modules identified as untested in the assessment. Each step is independently valuable and can be committed separately.