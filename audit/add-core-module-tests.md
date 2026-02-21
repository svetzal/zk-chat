```json
{ "severity": 3, "principle": "Tests Are the Executable Spec", "category": "Testing" }
```

## Assessment: Test Coverage Gaps Leave Core Behavior Unspecified

### The Numbers

| Metric | Value |
|--------|-------|
| Tests | **217 passed**, 0 failed ✅ |
| Lint | **0 warnings** ✅ |
| Coverage | **63%** ⚠️ |

### What's Working Well

This is a well-crafted project in many respects. The tests that *exist* are excellent — BDD-style `Describe`/`should_` naming, proper `Mock(spec=...)` usage, clean Arrange/Act/Assert separation, gateway-only mocking, and perfect co-location. The architecture is sound: service registry, gateway pattern, plugin system, functional core aspirations. Lint is pristine. Type hints are thorough. The code reads well.

### The Core Violation

**63% test coverage means 37% of the codebase has no executable specification.** This directly contradicts the principle that tests are the authoritative specification of system behavior. When tests don't cover a module, there is no verified contract for how it behaves — refactoring becomes risky, regressions go undetected, and the "executable spec" has gaps.

The most concerning under-tested modules are **not** the CLI entry points (those are imperative shell — harder to unit test, and that's acceptable). The real gaps are in **core infrastructure**:

| Module | Coverage | Concern |
|--------|----------|---------|
| `config.py` | 27% | Configuration loading/saving is critical — silent corruption here breaks everything |
| `git_gateway.py` | 35% | Gateway class — the *exact* kind of component the project's own guidelines say to mock and test |
| `vector_database.py` | 44% | Core search infrastructure — semantic search correctness depends on this |
| `zettelkasten.py` | 50% | The central domain class — half its behavior is unspecified |
| `service_provider.py` | 57% | Dependency resolution — failures here cascade to every plugin and tool |
| `mcp_tool_wrapper.py` | 33% | MCP integration bridge — type coercion bugs hide here |
| Several tools | 0% | `analyze_image`, `resolve_wikilink`, `iterative_problem_solving_agent` |

### Why This Matters Most

Among the principles, I considered:
- **No Knowledge Duplication** — `_merge_metadata()` is duplicated across `Zettelkasten` and `DocumentService` (a real issue, but localized)
- **Functional Core, Imperative Shell** — Some tools create services internally rather than receiving them (architectural inconsistency, but functional)
- **Tests Are the Executable Spec** — 63% coverage with critical modules undertested

The coverage gap wins because it has the **widest blast radius**. The duplicated metadata merging affects one function. The tool DI inconsistency is an aesthetic concern. But inadequate test coverage on `zettelkasten.py`, `config.py`, and `vector_database.py` means the three pillars of the system — document management, configuration, and search — can silently regress.

### How to Correct It

**Target: Raise coverage to ≥80% overall, with ≥90% on core modules.**

Prioritize in this order:

1. **`config.py` (27% → 90%+)** — Test `load()`, `load_or_initialize()`, edge cases for malformed YAML, missing files, migration paths. This is a pure data-loading module — trivial to test.

2. **`zettelkasten.py` (50% → 90%+)** — The untested 50% likely includes `reindex()`, `update_index()`, and document mutation paths. These are the most impactful behaviors. Mock the gateways (filesystem, vector DB) and specify the orchestration contracts.

3. **`vector_database.py` (44% → 85%+)** — Test collection creation, query behavior, embedding edge cases. Mock `ChromaGateway` at the boundary.

4. **`service_provider.py` (57% → 95%+)** — Test all service resolution paths, especially error cases when services aren't registered. This is pure logic — should be easy.

5. **`git_gateway.py` (35% → 80%+)** — As a gateway, test the wrapper logic (argument construction, output parsing). Mock the subprocess/git calls.

6. **0% tools** (`analyze_image`, `resolve_wikilink`) — Even a single happy-path test per tool dramatically improves confidence.

**Secondary fix:** Extract `_merge_metadata()` to a shared utility in `zk_chat/utils/` and delete the duplicate — this is a quick win for the "No Knowledge Duplication" principle and can be done safely once the test coverage supports it.

### One-Line Summary

The project writes *excellent* tests where it tests — it just doesn't test enough of its own core infrastructure to call those tests a reliable specification of system behavior.