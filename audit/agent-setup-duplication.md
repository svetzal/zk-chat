```json
{ "severity": 3, "principle": "No Knowledge Duplication", "category": "Simple Design Heuristics" }
```

## Assessment

This project is **generally well-crafted** — it uses Pydantic models consistently, follows the gateway pattern for I/O boundaries, has solid BDD-style tests with proper `Mock(spec=...)` usage, and maintains clean separation between services and tools. However, one principle violation stands out above the rest.

---

## Most Significant Violation: Knowledge Duplication in `agent.py`

**File:** `zk_chat/agent.py`, lines 88–142 vs 145–191

The functions `agent()` and `agent_single_query()` duplicate **~30 lines** of identical setup code. Both functions independently:

1. Build a service registry from config (lines 102/156)
2. Create a `ServiceProvider` (lines 103/157)
3. Extract the same 8 services from the provider (lines 105–112 / 159–166)
4. Call `_build_tools()` with identical parameters (lines 114–124 / 168–178)
5. Create an `MCPClientManager` context (lines 127/181)
6. Load the agent prompt from the same file (lines 130–132 / 184–186)
7. Construct the same `IterativeProblemSolvingAgent` (lines 134/188)

The **only** difference is the final behavior: one loops on `input()`, the other makes a single `solver.solve(query)` call.

This is the textbook case for Simple Design Heuristic #3: *"Avoid multiple spots that must change together for the same reason."* If you add a new service, change how tools are wired, modify MCP initialization, or alter the agent prompt loading — you **must** remember to change both functions identically.

### Recommended Fix

Extract the shared setup into a context manager or helper that yields a ready-to-use solver:

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


def agent(config: Config):
    # ... MCP verification stays here (only needed for interactive) ...
    with _create_agent(config) as solver:
        while True:
            query = input("Agent request: ")
            if not query:
                break
            print(solver.solve(query))


def agent_single_query(config: Config, query: str) -> str:
    with _create_agent(config) as solver:
        return solver.solve(query)
```

This reduces both callers to 3–5 lines and ensures there's **one place** that knows how to wire up an agent.

---

## Other Notable Findings (lower severity)

| Severity | Principle | Location | Issue |
|---|---|---|---|
| 2 | Functional Core / Imperative Shell | `global_config.py:42–69` | `os.path.abspath()` (queries CWD) in a model docstrings says is "pure data." Path resolution belongs at the caller. |
| 2 | No Knowledge Duplication | `console_service` in tools | Every tool independently defaults to `RichConsoleService()` when none is passed — should be wired through the service registry. |
| 2 | Test private methods | `document_service_spec.py:209–277`, `commit_changes_spec.py:137` | Tests call `_merge_metadata()` and `_generate_commit_message()` directly — violates own guidelines. |
| 1 | Test style consistency | 3 tool spec files | Use `test_*` functions instead of `Describe*/should_*` classes. |
| 2 | Mock library internals | `console_service_spec.py:39–56` | `@patch("zk_chat.console_service.Prompt")` mocks `rich` internals instead of treating `RichConsoleService` as the gateway boundary. |

The project is in good shape overall. The agent.py duplication is the single change that would yield the highest return on investment — it eliminates a maintenance trap and the fix is straightforward.