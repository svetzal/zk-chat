The plan is ready for your review. Here's a quick summary:

**8 steps, ~68 new tests, targeting ≥80% coverage** (up from 63%):

1. **`config.py`** — New spec file, 18 tests (0% → ~75%)
2. **`vector_database.py`** — New spec file, 7 tests (0% → ~90%)
3. **`zettelkasten.py`** — Extend existing spec, 16 tests (~20% → ~65%)
4. **`git_gateway.py`** — New spec file, 11 tests (0% → ~85%)
5. **Zero-coverage tools** — Two new spec files, 8 tests (0% → ~85% each)
6. **`service_provider.py`** — Extend existing spec, 4 tests (~60% → ~80%)
7. **`mcp_tool_wrapper.py`** — Extend existing spec, 4 tests (~33% → ~55%)
8. **Bonus refactor** — Extract duplicated `_merge_metadata` to shared utility

Each step is independently shippable and follows the project's existing BDD patterns.