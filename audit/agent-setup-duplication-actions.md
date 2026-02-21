All 13 steps are complete. Here's a summary of everything that was done:

---

## Summary of Changes

### Step 1 — `agent.py`: Eliminated knowledge duplication (Severity 3 — the primary fix)

Extracted a `_create_agent(config)` context manager that encapsulates all shared agent setup. Both `agent()` and `agent_single_query()` now call it, reducing each to 3–5 lines from ~30. A single place now knows how to wire up an agent — adding a new service or changing the prompt loading only needs to happen once.

### Step 3 — `global_config.py` + callers: Functional Core / Imperative Shell (Severity 2)

Removed all `os.path.abspath()` calls from `GlobalConfig` model methods (`add_bookmark`, `remove_bookmark`, `get_bookmark`, `set_last_opened_bookmark`). The model is now a pure data container. Added `os.path.abspath()` at the one `qt.py` call site that needed it (`save_settings`). Updated the spec to replace the relative-path test with a cleaner "stores path as given" test.

### Step 5 — Service registry + `agent.py`: Centralized `RichConsoleService` (Severity 2)

Added `CONSOLE_SERVICE` to `ServiceType`, `get_console_service()` to `ServiceProvider`, and registered a single `RichConsoleService` instance in `build_service_registry()`. `_build_tools()` now receives and passes the shared console service to all 16 tools, eliminating 16 independent `RichConsoleService()` instantiations.

### Step 7a — `document_service.py` + spec: No private method testing (Severity 2)

Extracted `_merge_metadata` as a public module-level function `merge_metadata()`. The `DescribeDocumentServiceMetadataMerging` test class was renamed to `DescribeMergeMetadata` and calls `merge_metadata()` directly — no private method access, no `document_service` fixture needed.

### Step 7b — `commit_changes_spec.py`: Remove private method test (Severity 2)

Removed `should_generate_commit_message_using_llm` which tested `_generate_commit_message()` directly. The behavior it covered is already verified by `should_successfully_commit_changes`.

### Step 9 — `console_service_spec.py`: No mocking of library internals (Severity 2)

Removed `should_provide_input_method_with_prompt` and `should_provide_input_method_without_prompt` which used `@patch("zk_chat.console_service.Prompt")` to mock Rich internals. `RichConsoleService` is the gateway boundary — its thin delegation to `rich` is not worth unit testing.

### Step 11 — 6 tool spec files: Consistent BDD test style (Severity 1)

Migrated all 6 files from bare `test_*` functions to `Describe*/should_*` classes: `read_zk_document_spec.py`, `delete_zk_document_spec.py`, `list_zk_documents_spec.py`, `create_or_overwrite_zk_document_spec.py`, `find_excerpts_related_to_spec.py`, `find_zk_documents_related_to_spec.py`.

**Final quality gate:** ✅ 261 tests pass, ✅ 0 ruff warnings, ✅ no known security vulnerabilities.