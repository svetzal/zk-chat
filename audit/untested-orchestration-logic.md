```json
{ "severity": 3, "principle": "Tests Are the Executable Spec", "category": "Testing" }
```

## Assessment: zk-chat

### What's Working Well

This is a well-crafted project. The positives are significant:

- **92% test coverage**, 261 tests all passing, zero ruff warnings
- **Excellent BDD style** — consistent `Describe`/`should_` naming, clean Arrange/Act/Assert
- **Strong gateway pattern** — `ChromaGateway`, `FilesystemGateway`, `GitGateway`, `ConfigGateway` all properly wrap I/O
- **Mock discipline** — `Mock(spec=ClassName)` used consistently, mocks target gateways not library internals
- **Pydantic everywhere** — zero `@dataclass` usage, all models are `BaseModel`
- **Clean service architecture** — constructor injection, single composition root, no service locator leakage
- **Active deduplication work** — recent commits explicitly target "No Knowledge Duplication"

### The Most Violated Principle: Tests Are the Executable Spec

The principle states: *"Correctness is non-negotiable"* and *"Tests verify behavior, not implementation details."* Where tests exist, they're excellent. The problem is **critical orchestration logic with zero test coverage**, hidden behind a reassuring 92% number.

#### Untested Business Logic

| Module | What It Does | Why It Matters |
|--------|-------------|----------------|
| `iterative_problem_solving_agent.py` | Iterative solve loop with DONE/FAIL/max-iterations exit conditions | Core agent behavior — a bug here breaks the agent silently |
| `mcp.py` (MCPServer) | Tool registration, request routing, JSON parsing, error handling | Protocol-level code where bugs cause mysterious failures |
| `resolve_wikilink.py` | Wikilink → file path resolution | Trivially testable, pure gateway delegation |
| `vector_database.py` | QueryResult transformation from raw Chroma responses (44% coverage) | Contains real mapping logic, not just I/O passthrough |
| `index.py` (reindex) | Full vs incremental reindex branching, progress tracking, config persistence | User-facing orchestration with multiple code paths |

#### Why 92% Is Misleading

The `testpaths = ["zk_chat"]` configuration only discovers spec files that happen to import these modules. Since nothing in test code imports `iterative_problem_solving_agent`, `mcp.py`, or `index.py`, **their lines aren't even measured**. The true coverage of business logic is lower than reported.

#### The `strip_thinking()` Example

In `iterative_problem_solving_agent.py` there's a **pure function** that strips `<think>` tags from text. This is the easiest possible thing to test — no mocks needed, pure input/output — yet it has no spec. When even the low-hanging fruit is untested, it signals these files were written outside the test-first discipline.

### How to Correct It

**Priority 1 — Make coverage honest:**
```bash
# Ensure ALL source files are measured, even unimported ones
uv run pytest --cov=zk_chat --cov-report=term-missing
```

**Priority 2 — Test the pure functions first (quick wins):**
- `strip_thinking()` — pure function, zero dependencies
- `ResolveWikiLink` — mock the filesystem gateway, verify path resolution

**Priority 3 — Test the orchestration logic:**
- `IterativeProblemSolvingAgent` — mock `ChatSession`, verify the DONE/FAIL/max-iterations exit conditions
- `MCPServer` — mock tool instances, verify request routing and error handling
- `VectorDatabase.query()` — mock `ChromaGateway`, verify the `QueryResult` transformation logic

**Priority 4 — Extract testable logic from `index.py`:**
- The `reindex()` function constructs its own `ServiceProvider` internally, making it hard to test. Extract the orchestration decisions (full vs incremental, which documents to process) into a pure function, then test that function.

**Design pattern to apply:** For each untested module, ask *"What decision does this code make?"* — that decision is what the test should verify. The I/O around it can stay untested in the gateway layer.