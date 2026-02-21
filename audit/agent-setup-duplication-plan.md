Now I have a thorough understanding of the codebase. Here is the complete step-by-step plan:

---

## Plan: Address Knowledge Duplication and Related Issues

### Step 1: Extract shared agent setup into a context manager in `agent.py` (Primary — Severity 3)

**File:** `zk_chat/agent.py`

**What to do:**

1. Create a new private context manager function `_create_agent(config: Config)` that encapsulates all shared setup logic currently duplicated between `agent()` (lines 102–134) and `agent_single_query()` (lines 156–188):

   - Build the service registry from config
   - Create a `ServiceProvider`
   - Extract all 8 services from the provider (gateway, filesystem_gateway, document_service, index_service, link_traversal_service, llm, smart_memory, git_gateway)
   - Call `_build_tools()` with those services
   - Open `MCPClientManager` context and extend tools with MCP tools
   - Load the agent prompt from `agent_prompt.txt`
   - Construct and yield the `IterativeProblemSolvingAgent` along with `llm` (since `agent()` uses `llm` in the solver constructor but it's already embedded)

   The context manager should use `contextlib.contextmanager` and yield the constructed `IterativeProblemSolvingAgent`. The `MCPClientManager` context must remain active while the agent is in use, so the `yield` must be inside the `with MCPClientManager()` block.

2. Simplify `agent(config: Config)` to:
   - Keep the MCP server verification logic (lines 89–100) — this is unique to the interactive mode
   - Call `with _create_agent(config) as solver:` and run the interactive `while True` / `input()` loop inside

3. Simplify `agent_single_query(config: Config, query: str)` to:
   - Call `with _create_agent(config) as solver:` and return `solver.solve(query)`

**Implementation detail for the context manager:**

```python
from contextlib import contextmanager

@contextmanager
def _create_agent(config: Config):
    """Build a fully-wired IterativeProblemSolvingAgent from config."""
    registry = build_service_registry(config)
    provider = ServiceProvider(registry)

    tools = _build_tools(
        config=config,
        filesystem_gateway=provider.get_filesystem_gateway(),
        document_service=provider.get_document_service(),
        index_service=provider.get_index_service(),
        link_traversal_service=provider.get_link_traversal_service(),
        llm=provider.get_llm_broker(),
        smart_memory=provider.get_smart_memory(),
        git_gateway=provider.get_git_gateway(),
        gateway=provider.get_model_gateway(),
    )

    with MCPClientManager() as mcp_manager:
        tools.extend(mcp_manager.get_tools())

        agent_prompt_path = Path(__file__).parent / "agent_prompt.txt"
        with open(agent_prompt_path) as f:
            agent_prompt = f.read()

        yield IterativeProblemSolvingAgent(
            llm=provider.get_llm_broker(),
            available_tools=tools,
            system_prompt=agent_prompt,
        )
```

Note: The intermediate local variables for each service (lines 105–112) are eliminated — we pass `provider.get_*()` directly to `_build_tools()`. This is safe because `_build_tools` only uses them to construct tools, it doesn't call them multiple times.

**Add the `contextmanager` import** to the existing imports at the top of the file:
```python
from contextlib import contextmanager
```

**Resulting `agent()` function:**
```python
def agent(config: Config):
    from zk_chat.global_config_gateway import GlobalConfigGateway

    global_config = GlobalConfigGateway().load()
    if global_config.list_mcp_servers():
        print("Verifying MCP server availability...")
        unavailable = verify_all_mcp_servers()
        if unavailable:
            print("\nWarning: The following MCP servers are unavailable:")
            for name in unavailable:
                print(f"  - {name}")
            print("\nYou can continue, but these servers will not be accessible during the session.")
            print("Use 'zk-chat mcp verify' to check server status or 'zk-chat mcp list' to see all servers.\n")

    with _create_agent(config) as solver:
        while True:
            query = input("Agent request: ")
            if not query:
                break
            else:
                response = solver.solve(query)
                print(response)
```

**Resulting `agent_single_query()` function:**
```python
def agent_single_query(config: Config, query: str) -> str:
    """
    Execute a single query using the agent and return the response.

    Args:
        config: Configuration object
        query: The query string to process

    Returns:
        The agent's response as a string
    """
    with _create_agent(config) as solver:
        return solver.solve(query)
```

### Step 2: Run tests and linting to verify the refactor

**Commands:**
```bash
ruff check zk_chat/agent.py
pytest zk_chat/ -x
```

Ensure all existing tests still pass. The `agent.py` module does not have its own spec file (it's hard to unit test due to interactive I/O and heavy integration), so correctness is verified by ensuring no import errors and all downstream tests pass.

### Step 3: Move `os.path.abspath()` out of `GlobalConfig` model methods (Severity 2)

**File:** `zk_chat/global_config.py`

**Problem:** The `GlobalConfig` class docstring says it is a "pure data model" but four methods call `os.path.abspath()`, which queries the current working directory (an I/O side effect). This makes the methods impure and environment-dependent.

**What to do:**

1. Remove the `os.path.abspath()` calls from these four methods in `GlobalConfig`:
   - `add_bookmark()` (line 44)
   - `remove_bookmark()` (line 49)
   - `get_bookmark()` (line 60)
   - `set_last_opened_bookmark()` (line 65)

   Each method should operate directly on the `vault_path` parameter as passed in, without resolving it. The methods become truly pure — same input always produces same output.

2. Move the `os.path.abspath()` responsibility to callers. Search for all call sites of these four methods and ensure the callers pass already-resolved absolute paths. The callers (CLI commands, GUI handlers) are at the imperative shell boundary where I/O like path resolution is appropriate.

   Search for callers with:
   ```
   grep -rn "add_bookmark\|remove_bookmark\|get_bookmark\|set_last_opened_bookmark" zk_chat/
   ```

   At each call site, wrap the `vault_path` argument in `os.path.abspath()` before passing it.

3. Remove `import os` from `global_config.py` if it's no longer used.

4. Update the `global_config_spec.py` test `should_resolve_relative_paths_to_absolute` — this test verifies the old behavior where the model resolves paths. Either:
   - Remove this test (since the model no longer resolves paths), or
   - Change it to verify the model stores paths exactly as given (i.e., if you pass `"."`, it stores `"."`), and add a test at the caller level that verifies the caller resolves paths before passing them.

### Step 4: Run tests and linting to verify GlobalConfig changes

**Commands:**
```bash
ruff check zk_chat/global_config.py
pytest zk_chat/global_config_spec.py -v
pytest zk_chat/ -x
```

### Step 5: Wire `RichConsoleService` through the service registry (Severity 2)

**Problem:** Every tool independently defaults to `RichConsoleService()` when none is passed (`self.console_service = console_service or RichConsoleService()`). This means there are ~16 independent instantiations of `RichConsoleService` — one per tool. While this isn't strictly "knowledge duplication" in the DRY sense (the decision to use `RichConsoleService` as the default is the same everywhere), it means the console service cannot be centrally configured or replaced.

**What to do:**

1. **Add `CONSOLE_SERVICE` to `ServiceType` enum** in `zk_chat/services/service_registry.py`:
   ```python
   CONSOLE_SERVICE = "console_service"
   ```

2. **Add `get_console_service()` to `ServiceProvider`** in `zk_chat/services/service_provider.py`:
   ```python
   def get_console_service(self):
       """Get the console service."""
       from zk_chat.console_service import RichConsoleService
       return self._registry.get_service(ServiceType.CONSOLE_SERVICE, RichConsoleService)
   ```

3. **Register `RichConsoleService` in `build_service_registry()`** in `zk_chat/service_factory.py`:
   ```python
   from zk_chat.console_service import RichConsoleService

   console_service = RichConsoleService()
   registry.register_service(ServiceType.CONSOLE_SERVICE, console_service)
   ```

4. **Pass the console service from the registry into `_build_tools()`** in `zk_chat/agent.py`:
   - Add `console_service` parameter to `_build_tools()`
   - Pass `console_service` to each tool constructor that accepts it
   - In `_create_agent()`, get it from the provider: `provider.get_console_service()`

5. **Update each tool constructor** to still accept `console_service` as an optional parameter (for backward compatibility in tests), but now it gets passed from the registry during normal operation rather than each tool creating its own. The `or RichConsoleService()` fallback can remain for test convenience but won't be exercised during normal app execution.

**Affected tool files (all in `zk_chat/tools/`):**
- `read_zk_document.py`
- `delete_zk_document.py`
- `list_zk_documents.py`
- `rename_zk_document.py`
- `create_or_overwrite_zk_document.py`
- `find_zk_documents_related_to.py`
- `find_excerpts_related_to.py`
- `find_backlinks.py`
- `find_forward_links.py`
- `store_in_smart_memory.py`
- `retrieve_from_smart_memory.py`
- `analyze_image.py`
- `commit_changes.py`
- `uncommitted_changes.py`
- `list_zk_images.py`
- `resolve_wikilink.py`

### Step 6: Run tests and linting to verify console service wiring

**Commands:**
```bash
ruff check zk_chat/
pytest zk_chat/ -x
```

### Step 7: Refactor tests that call private methods directly (Severity 2)

**Problem:** The project's own AGENTS.md says "Do not test private methods directly (those starting with `_`) — test through the public API." Two spec files violate this.

#### 7a: `zk_chat/services/document_service_spec.py` — `_merge_metadata` tests

**File:** `zk_chat/services/document_service_spec.py`, class `DescribeDocumentServiceMetadataMerging` (lines 209–277)

**What to do:**

The `_merge_metadata` method is called by two public methods: `append_to_document()` and `update_document_metadata()`. The 7 tests currently call `document_service._merge_metadata()` directly.

**Option A (Recommended — extract to pure function):** Since `_merge_metadata` is a pure function (no side effects, doesn't use `self` beyond recursive calls), extract it as a module-level pure function `merge_metadata()` (no underscore, public). Then:
- Tests can call it directly (it's now a public function, not a private method)
- `DocumentService.append_to_document()` and `update_document_metadata()` call the module-level function
- The existing tests become tests of a pure public function — no violation

Update the test class name from `DescribeDocumentServiceMetadataMerging` to `DescribeMergeMetadata` and change calls from `document_service._merge_metadata(...)` to `merge_metadata(...)`. The `document_service` fixture is no longer needed for these tests.

**Option B (Alternative — test through public API):** Rewrite the 7 tests to call `update_document_metadata()` and assert the merged result via the `filesystem_gateway.write_markdown` mock's call args. This is more coupled to the implementation flow but tests behavior through the public API.

**Recommendation:** Option A — the function is genuinely a pure utility, and extracting it makes the code clearer.

#### 7b: `zk_chat/tools/commit_changes_spec.py` — `_generate_commit_message` test

**File:** `zk_chat/tools/commit_changes_spec.py`, method `should_generate_commit_message_using_llm` (line 131–144)

**What to do:**

This test calls `commit_changes._generate_commit_message(test_diff_summary)` directly. The `_generate_commit_message` is already indirectly tested through the `should_commit_changes_successfully` test (which calls `run()` and verifies the full flow including commit message generation).

**Action:** Delete the `should_generate_commit_message_using_llm` test method entirely. The behavior it tests is already covered by `should_commit_changes_successfully` which verifies that `mock_llm_broker.generate.assert_called_once()` and `mock_git_gateway.commit.assert_called_once_with("Test commit message")`.

If there's value in verifying the prompt format sent to the LLM, add an assertion to the existing `should_commit_changes_successfully` test that inspects the `mock_llm_broker.generate` call args.

### Step 8: Run tests to verify test refactoring

**Commands:**
```bash
pytest zk_chat/services/document_service_spec.py -v
pytest zk_chat/tools/commit_changes_spec.py -v
pytest zk_chat/ -x
```

### Step 9: Fix `console_service_spec.py` mocking of library internals (Severity 2)

**File:** `zk_chat/console_service_spec.py`, lines 39 and 49

**Problem:** `@patch("zk_chat.console_service.Prompt")` mocks `rich.prompt.Prompt` — a library internal. Per the project's guidelines, `RichConsoleService` IS the gateway boundary for Rich. Tests of a gateway should not mock the library behind it (gateways are thin wrappers not worth unit testing), OR if they must be tested, they should test observable output behavior.

**What to do:**

The two tests `should_provide_input_method_with_prompt` and `should_provide_input_method_without_prompt` verify that `RichConsoleService.input()` delegates to `Prompt.ask()` — this is testing the implementation of the gateway, not its behavior.

**Action:** Remove these two tests. The `RichConsoleService` is a gateway class (thin wrapper around `rich`). Per the project's own guidelines: "Do not test gateway (I/O isolating) classes unless they have custom logic, and if they do favour moving that logic into the core." There is no custom logic in the `input()` method — it's a straight delegation.

The remaining tests (`should_be_instantiated_with_theme_and_console`, `should_include_chat_theme_colors`, `should_include_banner_theme_colors`, `should_provide_print_method`, `should_provide_access_to_console_instance`) can remain. The `should_provide_print_method` test (line 59–65) does mock `service.console` directly on the instance, which is borderline but acceptable since it's testing the wrapper's delegation.

Also remove the `from unittest.mock import Mock, patch` import's `patch` if no longer used (keep `Mock` if still used by `should_provide_print_method`).

### Step 10: Run tests and linting after console_service_spec changes

**Commands:**
```bash
pytest zk_chat/console_service_spec.py -v
ruff check zk_chat/console_service_spec.py
```

### Step 11: Migrate tool spec files from `test_*` to `Describe*/should_*` style (Severity 1)

**Problem:** Six tool spec files use bare `test_*` functions instead of the project's BDD `Describe*/should_*` pattern:

1. `zk_chat/tools/read_zk_document_spec.py`
2. `zk_chat/tools/delete_zk_document_spec.py`
3. `zk_chat/tools/list_zk_documents_spec.py`
4. `zk_chat/tools/create_or_overwrite_zk_document_spec.py`
5. `zk_chat/tools/find_excerpts_related_to_spec.py`
6. `zk_chat/tools/find_zk_documents_related_to_spec.py`

**What to do for each file:**

1. Wrap all `test_*` functions in a `Describe<ToolName>:` class
2. Rename each `test_*` function to `should_*` method, using descriptive behavior names
3. Convert module-level `@pytest.fixture` definitions to class-level fixtures (or keep them module-level if shared)
4. Keep the Arrange/Act/Assert structure with blank line separators
5. Ensure all `Mock(spec=...)` patterns are preserved

**Example transformation for `read_zk_document_spec.py`:**

Before:
```python
def test_read_document_when_exists(read_tool, mock_filesystem):
    ...
```

After:
```python
class DescribeReadZkDocument:
    def should_return_document_json_when_exists(self, read_tool, mock_filesystem):
        ...
```

### Step 12: Run full test suite and linting as final verification

**Commands:**
```bash
ruff check zk_chat/
ruff format zk_chat/
pytest zk_chat/ -v
pytest zk_chat/ --cov
```

Ensure:
- Zero ruff warnings
- All tests pass
- Coverage is not degraded (removing tests of private methods and gateway internals may slightly reduce line coverage, but the coverage of meaningful behavior should remain the same)

### Step 13: Run security audit

**Commands:**
```bash
uvx pip-audit
```

This is a standing quality gate requirement per AGENTS.md.

---

## Summary of Changes by File

| File | Change | Step |
|---|---|---|
| `zk_chat/agent.py` | Extract `_create_agent()` context manager, simplify `agent()` and `agent_single_query()` | 1 |
| `zk_chat/global_config.py` | Remove `os.path.abspath()` from model methods, push to callers | 3 |
| `zk_chat/global_config_spec.py` | Update/remove `should_resolve_relative_paths_to_absolute` test | 3 |
| Callers of `GlobalConfig.add_bookmark()` etc. | Add `os.path.abspath()` at call sites | 3 |
| `zk_chat/services/service_registry.py` | Add `CONSOLE_SERVICE` to `ServiceType` | 5 |
| `zk_chat/services/service_provider.py` | Add `get_console_service()` method | 5 |
| `zk_chat/service_factory.py` | Register `RichConsoleService` in registry | 5 |
| `zk_chat/agent.py` (`_build_tools`) | Pass console service to tool constructors | 5 |
| `zk_chat/services/document_service.py` | Extract `_merge_metadata` as public module-level function | 7a |
| `zk_chat/services/document_service_spec.py` | Update tests to call public `merge_metadata()` | 7a |
| `zk_chat/tools/commit_changes_spec.py` | Remove `should_generate_commit_message_using_llm` test | 7b |
| `zk_chat/console_service_spec.py` | Remove two tests that `@patch` Rich internals | 9 |
| 6 tool `*_spec.py` files | Migrate from `test_*` to `Describe*/should_*` BDD style | 11 |