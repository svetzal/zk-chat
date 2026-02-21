Now I have a complete picture. Here is the detailed plan:

---

## Plan: Centralize Composition Root to Eliminate Duplicated Service Wiring

### Problem Summary

The knowledge of "how to create a model gateway from a Config" is duplicated 7 times, and "how to wire up the full service graph" is duplicated 4+ times. The project already has `ServiceRegistry` and `ServiceProvider` infrastructure that is tested but **never used in production**. The duplicates have already diverged (inconsistent comparison styles, inconsistent error handling, inconsistent feature sets).

---

### Step 1: Create `create_model_gateway()` — the single gateway factory function

**File:** `zk_chat/gateway_factory.py` (new file)

Create a single, shared function that encapsulates the "which gateway to create" decision. This is the most duplicated piece (7 locations).

```python
"""Factory for creating model gateways based on configuration."""
import os

from mojentic.llm.gateways import OllamaGateway, OpenAIGateway

from zk_chat.config import ModelGateway


def create_model_gateway(gateway: ModelGateway) -> OllamaGateway | OpenAIGateway:
    """Create the appropriate LLM gateway based on the configured gateway type.

    Parameters
    ----------
    gateway : ModelGateway
        The gateway type to create (OLLAMA or OPENAI).

    Returns
    -------
    OllamaGateway | OpenAIGateway
        The configured gateway instance.

    Raises
    ------
    ValueError
        If the gateway type is not recognized.
    """
    match gateway:
        case ModelGateway.OLLAMA:
            return OllamaGateway()
        case ModelGateway.OPENAI:
            return OpenAIGateway(os.environ.get("OPENAI_API_KEY"))
        case _:
            raise ValueError(f"Unsupported gateway type: {gateway}")
```

**Design decisions:**
- Uses `match` statement (Python 3.10+; project requires 3.11+)
- Accepts `ModelGateway` enum directly (not `Config`), keeping it minimal
- **Raises `ValueError`** on unknown gateway (consistent error handling — no silent fallbacks)
- Located in its own module to avoid circular imports (config.py imports gateway classes, and we don't want gateway_factory to be in config.py alongside `Config` which is a data class)

**Test file:** `zk_chat/gateway_factory_spec.py`

Write BDD-style tests covering:
- `should_create_ollama_gateway_for_ollama_config`
- `should_create_openai_gateway_for_openai_config`
- `should_raise_value_error_for_unknown_gateway` (use a mock/invalid value)

All tests mock `OllamaGateway` and `OpenAIGateway` constructors (or simply check `isinstance`) to avoid needing real gateway connections.

---

### Step 2: Create `build_service_registry()` — the single composition root

**File:** `zk_chat/service_factory.py` (new file)

Create a factory function that takes a `Config` and returns a fully populated `ServiceRegistry`. This replaces all the manual wiring scattered across entry points.

```python
"""Factory for building the application service registry from configuration."""
import os

from mojentic.llm import LLMBroker
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import Config
from zk_chat.gateway_factory import create_model_gateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.services.document_service import DocumentService
from zk_chat.services.index_service import IndexService
from zk_chat.services.link_traversal_service import LinkTraversalService
from zk_chat.services.service_registry import ServiceRegistry, ServiceType
from zk_chat.tools.git_gateway import GitGateway
from zk_chat.vector_database import VectorDatabase


def build_service_registry(config: Config) -> ServiceRegistry:
    """Build a fully-wired ServiceRegistry from configuration.

    Creates all core services (gateway, chroma, vector databases, document service,
    index service, link traversal, LLM broker, smart memory, git gateway) and
    registers them in a ServiceRegistry.

    Parameters
    ----------
    config : Config
        The application configuration.

    Returns
    -------
    ServiceRegistry
        A fully populated service registry.
    """
    registry = ServiceRegistry()

    # Configuration
    registry.register_service(ServiceType.CONFIG, config)

    # Model gateway
    gateway = create_model_gateway(config.gateway)
    registry.register_service(ServiceType.MODEL_GATEWAY, gateway)

    # ChromaDB gateway
    db_dir = os.path.join(config.vault, ".zk_chat_db")
    chroma_gateway = ChromaGateway(config.gateway, db_dir=db_dir)
    registry.register_service(ServiceType.CHROMA_GATEWAY, chroma_gateway)

    # Vector databases
    excerpts_db = VectorDatabase(
        chroma_gateway=chroma_gateway,
        gateway=gateway,
        collection_name=ZkCollectionName.EXCERPTS,
    )
    documents_db = VectorDatabase(
        chroma_gateway=chroma_gateway,
        gateway=gateway,
        collection_name=ZkCollectionName.DOCUMENTS,
    )

    # Filesystem gateway
    filesystem_gateway = MarkdownFilesystemGateway(config.vault)
    registry.register_service(ServiceType.FILESYSTEM_GATEWAY, filesystem_gateway)

    # Tokenizer gateway
    tokenizer_gateway = TokenizerGateway()
    registry.register_service(ServiceType.TOKENIZER_GATEWAY, tokenizer_gateway)

    # Core services
    document_service = DocumentService(filesystem_gateway)
    registry.register_service(ServiceType.DOCUMENT_SERVICE, document_service)

    index_service = IndexService(
        tokenizer_gateway=tokenizer_gateway,
        excerpts_db=excerpts_db,
        documents_db=documents_db,
        filesystem_gateway=filesystem_gateway,
    )
    registry.register_service(ServiceType.INDEX_SERVICE, index_service)

    link_traversal_service = LinkTraversalService(filesystem_gateway)
    registry.register_service(ServiceType.LINK_TRAVERSAL_SERVICE, link_traversal_service)

    # LLM broker
    llm_broker = LLMBroker(config.model, gateway=gateway)
    registry.register_service(ServiceType.LLM_BROKER, llm_broker)

    # Smart memory
    smart_memory = SmartMemory(chroma_gateway=chroma_gateway, gateway=gateway)
    registry.register_service(ServiceType.SMART_MEMORY, smart_memory)

    # Git gateway
    git_gateway = GitGateway(config.vault)
    registry.register_service(ServiceType.GIT_GATEWAY, git_gateway)

    return registry
```

**Design decisions:**
- Returns `ServiceRegistry` (not `ServiceProvider`) — callers can wrap it in a `ServiceProvider` if they need the convenience getters
- Wires **all** services. Entry points that only need a subset simply ignore the rest (no cost — the services are lightweight to construct)
- Single place to add new services in the future

**Test file:** `zk_chat/service_factory_spec.py`

Write BDD-style tests covering:
- `should_register_config_in_registry`
- `should_register_model_gateway_in_registry`
- `should_register_chroma_gateway_in_registry`
- `should_register_filesystem_gateway_in_registry`
- `should_register_document_service_in_registry`
- `should_register_index_service_in_registry`
- `should_register_link_traversal_service_in_registry`
- `should_register_llm_broker_in_registry`
- `should_register_smart_memory_in_registry`
- `should_register_git_gateway_in_registry`

Tests should mock `create_model_gateway` (it's a gateway — tested separately) and verify the correct `ServiceType` keys are populated. Use `Mock(spec=...)` for the gateway classes.

---

### Step 3: Update `zk_chat/agent.py` — replace both `agent()` and `agent_single_query()`

**3a. Update `agent()` function (lines 115–158)**

Replace the manual wiring block (lines 115–158) with:

```python
from zk_chat.service_factory import build_service_registry
from zk_chat.services.service_provider import ServiceProvider

registry = build_service_registry(config)
provider = ServiceProvider(registry)

gateway = provider.get_model_gateway()
filesystem_gateway = provider.get_filesystem_gateway()
document_service = provider.get_document_service()
index_service = provider.get_index_service()
link_traversal_service = provider.get_link_traversal_service()
llm = provider.get_llm_broker()
smart_memory = provider.get_smart_memory()
git_gateway = provider.get_git_gateway()
```

The rest of the function (MCP loading, `_build_tools`, agent loop) stays the same — it still passes these variables to `_build_tools()`. No changes needed to `_build_tools()` itself.

**3b. Update `agent_single_query()` function (lines 192–231)**

Same replacement — extract the variables from the registry/provider instead of constructing them inline. The function body from `tools = _build_tools(...)` onward stays unchanged.

**3c. Fix the `.value` comparison inconsistency**

The old code `config.gateway.value == ModelGateway.OLLAMA` is removed entirely since the gateway selection now lives in `create_model_gateway()`.

**3d. Clean up unused imports**

Remove the now-unused direct imports from `agent.py`:
- `ChromaGateway`
- `OllamaGateway`, `OpenAIGateway`
- `TokenizerGateway`
- `MarkdownFilesystemGateway`
- `VectorDatabase`
- `ZkCollectionName`
- `SmartMemory`
- `DocumentService`
- `IndexService`
- `LinkTraversalService`
- `GitGateway`

Keep imports that are still used directly (e.g., `LLMBroker` if used in `_build_tools` for `AnalyzeImage`).

**Note:** `_build_tools` creates `LLMBroker(model=config.visual_model, gateway=gateway)` for `AnalyzeImage` — this is a separate LLM broker for the visual model and is intentionally NOT in the registry. This is fine; it's tool-specific construction that doesn't belong in the general service graph.

---

### Step 4: Update `zk_chat/qt.py` — replace `initialize_chat_session()`

**Lines 397–446**: Replace the manual wiring (lines 398–425) with:

```python
from zk_chat.service_factory import build_service_registry
from zk_chat.services.service_provider import ServiceProvider

registry = build_service_registry(self.config)
provider = ServiceProvider(registry)

gateway = provider.get_model_gateway()
filesystem_gateway = provider.get_filesystem_gateway()
document_service = provider.get_document_service()
index_service = provider.get_index_service()
chat_llm = provider.get_llm_broker()
```

The tool list construction (lines 428–440) stays the same — the Qt GUI intentionally uses a subset of tools. This is a **feature decision**, not knowledge duplication. The Qt GUI provides a read-only research assistant experience, so it only exposes search and read tools.

**Clean up unused imports** from qt.py:
- `ChromaGateway`, `OllamaGateway`, `OpenAIGateway`, `TokenizerGateway`
- `VectorDatabase`, `ZkCollectionName`
- `MarkdownFilesystemGateway`

**Error handling change:** The old code silently defaulted to Ollama. Now `create_model_gateway()` raises `ValueError`. This is **correct** — if the config has an invalid gateway, we should fail fast, not silently use the wrong backend. The Qt GUI can catch this at a higher level if needed.

---

### Step 5: Update `zk_chat/index.py` — replace `_make_gateway()` and `_build_index_service()`

**5a. Remove `_make_gateway()` (lines 20–25)** — replaced by `create_model_gateway()`.

**5b. Remove `_build_index_service()` (lines 28–42)** — the IndexService is now created by `build_service_registry()`.

**5c. Update `reindex()` (lines 95–100):**

Replace:
```python
db_dir = os.path.join(config.vault, ".zk_chat_db")
chroma = ChromaGateway(config.gateway, db_dir=db_dir)
gateway = _make_gateway(config)
index_service = _build_index_service(config, chroma, gateway)
```

With:
```python
from zk_chat.service_factory import build_service_registry
from zk_chat.services.service_provider import ServiceProvider

registry = build_service_registry(config)
provider = ServiceProvider(registry)
index_service = provider.get_index_service()
```

The rest of the function (progress tracking, full vs incremental reindex, saving config) stays unchanged.

**Clean up unused imports:**
- `OllamaGateway`, `OpenAIGateway`, `TokenizerGateway`
- `ChromaGateway`, `VectorDatabase`, `ZkCollectionName`
- `MarkdownFilesystemGateway`

---

### Step 6: Update `zk_chat/cli.py` — replace `_reset_smart_memory()`

**Lines 211–223**: Replace the manual wiring with:

```python
def _reset_smart_memory(vault_path: str, config: Config) -> None:
    """Reset SmartMemory for the vault."""
    from zk_chat.service_factory import build_service_registry
    from zk_chat.services.service_provider import ServiceProvider

    registry = build_service_registry(config)
    provider = ServiceProvider(registry)
    memory = provider.get_smart_memory()
    memory.reset()
    print("Smart memory has been reset.")
```

**Clean up unused imports:**
- `ChromaGateway`, `OllamaGateway`, `OpenAIGateway`
- `SmartMemory`

---

### Step 7: Update `zk_chat/commands/diagnose.py` — replace `_make_gateway()`

**7a. Remove `_make_gateway()` (lines 67–72)** — replaced by `create_model_gateway()`.

**7b. Update `index()` command (lines 187–211):**

Replace lines 202–203:
```python
chroma = ChromaGateway(config.gateway, db_dir=db_dir)
gateway = _make_gateway(config)
```

With:
```python
from zk_chat.gateway_factory import create_model_gateway

chroma = ChromaGateway(config.gateway, db_dir=db_dir)
gateway = create_model_gateway(config.gateway)
```

**Note:** For `diagnose.py`, we do NOT use the full `build_service_registry()` because the diagnostic functions call individual services in an unusual way (e.g., `_test_embedding(gateway)` tests the raw gateway, `_run_test_query()` builds an IndexService to test queries). The key fix here is just centralizing `_make_gateway()` → `create_model_gateway()`.

**7c. Update `_run_test_query()` (lines 123–162):**

This function manually constructs an `IndexService`. We have two options:
- Option A: Accept a `ServiceProvider` instead of raw `config`/`chroma`/`gateway`
- Option B: Leave it constructing `IndexService` locally since it's diagnostic code

**Choose Option A** — update `_run_test_query` to accept the registry:

```python
from zk_chat.service_factory import build_service_registry
from zk_chat.services.service_provider import ServiceProvider

# In index() command:
registry = build_service_registry(config)
provider = ServiceProvider(registry)
gateway = provider.get_model_gateway()
chroma = provider.get_chroma_gateway()
```

Then pass `provider` to `_run_test_query` instead of `config`/`chroma`/`gateway`, and use `provider.get_index_service()`.

**Clean up unused imports:**
- `OllamaGateway`, `OpenAIGateway`
- `TokenizerGateway`
- `VectorDatabase`, `ZkCollectionName`
- `MarkdownFilesystemGateway`

---

### Step 8: Update `zk_chat/config.py` — replace gateway creation in `get_available_models()`

**Lines 15–24**: Replace with:

```python
def get_available_models(gateway: ModelGateway = ModelGateway.OLLAMA) -> list[str]:
    from zk_chat.gateway_factory import create_model_gateway

    try:
        g = create_model_gateway(gateway)
    except ValueError as e:
        print(f"Error: {e}")
        return []
    return g.get_available_models()
```

**Design decision:** This function is used for interactive model selection — it makes sense to catch the `ValueError` and return an empty list with an error message, since the caller (`select_model()`) already handles empty model lists gracefully.

**Clean up unused imports:**
- Remove `OllamaGateway`, `OpenAIGateway` from config.py imports
- Remove `import os` if no longer used (check: it's still used in `get_config_path()` and `Config.load()`, so keep it)

---

### Step 9: Update `zk_chat/services/__init__.py` — export the new factory

Add the factory to the services package exports so it's easily discoverable:

```python
from zk_chat.gateway_factory import create_model_gateway
from zk_chat.service_factory import build_service_registry
```

And add to `__all__`:
```python
'create_model_gateway',
'build_service_registry',
```

---

### Step 10: Run the full quality gate

1. **Run all tests:** `pytest` — ensure all existing 425+ specs still pass, plus the new specs for `gateway_factory` and `service_factory`
2. **Run linting:** `ruff check zk_chat` — ensure zero warnings
3. **Run formatting:** `ruff format zk_chat` — ensure consistent formatting
4. **Run security audit:** `uvx pip-audit` — check for vulnerabilities

---

### Step 11: Clean up and verify

1. **Verify no remaining duplicates:** Search for `OllamaGateway()` and `OpenAIGateway(` across the codebase. The only occurrences should be in `gateway_factory.py` and its test.
2. **Verify no remaining inline wiring:** Search for `ChromaGateway(config` and `VectorDatabase(chroma_gateway=` patterns. The only occurrences should be in `service_factory.py` and its test.
3. **Verify the `index.py:main()` function** — it still needs to parse args and create a Config, but the gateway/service wiring should now flow through the factory.
4. **Verify `diagnose.py` still works** — the diagnostic flow tests raw gateway access and individual services, which should still work through the provider.

---

### Files Modified (Summary)

| File | Action |
|------|--------|
| `zk_chat/gateway_factory.py` | **NEW** — Single gateway creation function |
| `zk_chat/gateway_factory_spec.py` | **NEW** — Tests for gateway factory |
| `zk_chat/service_factory.py` | **NEW** — Single composition root |
| `zk_chat/service_factory_spec.py` | **NEW** — Tests for service factory |
| `zk_chat/agent.py` | **MODIFIED** — Use factory in `agent()` and `agent_single_query()` |
| `zk_chat/qt.py` | **MODIFIED** — Use factory in `initialize_chat_session()` |
| `zk_chat/index.py` | **MODIFIED** — Use factory in `reindex()`, remove `_make_gateway` and `_build_index_service` |
| `zk_chat/cli.py` | **MODIFIED** — Use factory in `_reset_smart_memory()` |
| `zk_chat/commands/diagnose.py` | **MODIFIED** — Use `create_model_gateway()`, use provider in diagnostic functions |
| `zk_chat/config.py` | **MODIFIED** — Use `create_model_gateway()` in `get_available_models()` |
| `zk_chat/services/__init__.py` | **MODIFIED** — Export new factories |

### Risk Assessment

- **Low risk:** The refactoring preserves all existing behavior. Each entry point will construct the same objects via the factory that it previously constructed inline.
- **One behavioral change:** Silent Ollama fallbacks (in `qt.py`, `cli.py`, `index.py`, `diagnose.py`) become `ValueError` raises. This is **intentional** — silent fallbacks mask configuration errors. If this is undesirable for any entry point, we can catch the `ValueError` explicitly at the call site.
- **No API changes:** No public interfaces change. The `Config` class, CLI commands, and tool signatures are all unchanged.