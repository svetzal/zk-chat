All quality gates pass. Here's a summary of what was done:

---

## Summary

### Problem Eliminated

The knowledge of *"which gateway to create from a ModelGateway config value"* was duplicated **7 times** across the codebase, and full service wiring was duplicated **4+ times**. These copies had already diverged (inconsistent `.value` comparisons in `agent.py`, silent Ollama fallbacks in `qt.py`/`cli.py`/`index.py`/`diagnose.py`, different error handling in `config.py`).

### New Files Created

| File | Purpose |
|------|---------|
| `zk_chat/gateway_factory.py` | Single `create_model_gateway()` function — the one place that decides `OllamaGateway` vs `OpenAIGateway`. Uses `match` statement, raises `ValueError` on unknown gateway (no silent fallbacks). |
| `zk_chat/gateway_factory_spec.py` | 4 BDD tests: Ollama creation, OpenAI creation, API key threading, invalid gateway error. |
| `zk_chat/service_factory.py` | Single `build_service_registry()` — the composition root. Wires all 11 service types into the existing `ServiceRegistry` infrastructure that was previously only used in tests. |
| `zk_chat/service_factory_spec.py` | 12 BDD tests: verifies every `ServiceType` is registered, verifies `create_model_gateway` is delegated to correctly. |

### Files Modified

| File | Change |
|------|--------|
| `agent.py` | Removed 7 manual wiring imports + both inline wiring blocks → 3 lines each using `build_service_registry` + `ServiceProvider`. Fixed the `.value` comparison bug. |
| `qt.py` | Removed 7 unused imports; `initialize_chat_session` wiring → `build_service_registry` + `ServiceProvider`. |
| `index.py` | Deleted `_make_gateway()` and `_build_index_service()` private functions; `reindex()` → 3-line factory call. |
| `cli.py` | `_reset_smart_memory()` reduced from 13 lines to 5 lines using the factory. |
| `commands/diagnose.py` | Deleted local `_make_gateway()`; `_run_test_query` now accepts `ServiceProvider`; `index` command uses `build_service_registry`. |
| `config.py` | `get_available_models()` now delegates to `create_model_gateway()` instead of re-implementing the selection. |

### Quality Gate Results
- ✅ **227 tests passed** (0 failures, 16 new tests added)
- ✅ **`ruff check zk_chat`** — zero warnings
- ✅ **`pip-audit`** — no known vulnerabilities