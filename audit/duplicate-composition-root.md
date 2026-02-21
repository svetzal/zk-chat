Now I have the complete picture. Here is my assessment:

```json
{ "severity": 3, "principle": "No Knowledge Duplication", "category": "Simple Design Heuristics" }
```

## Assessment: Duplicated Composition Root

### The Violation

The project's most significant principle violation is **No Knowledge Duplication** — specifically, the knowledge of *how to wire up the application's dependency graph from a `Config`* is expressed **7 times** across the codebase.

### The Evidence

**Gateway selection** (deciding `OllamaGateway` vs `OpenAIGateway`) is copy-pasted in 7 locations:

| File | Lines | Notes |
|------|-------|-------|
| `agent.py` `agent()` | 118–123 | Uses `.value` comparison (subtly different) |
| `agent.py` `agent_single_query()` | 195–200 | Uses `.value` comparison |
| `qt.py` `initialize_chat_session()` | 402–408 | Silently defaults to Ollama |
| `cli.py` `_reset_smart_memory()` | 215–220 | Silently defaults to Ollama |
| `index.py` `_make_gateway()` | 20–25 | Returns Ollama as fallback |
| `config.py` `get_available_models()` | 16–24 | Different error handling (prints, returns empty) |
| `commands/diagnose.py` | 69–72 | Returns Ollama as fallback |

**Full service wiring** (ChromaGateway → VectorDatabase → DocumentService → IndexService etc.) is duplicated across at least 4 locations: `agent()`, `agent_single_query()`, `qt.py:initialize_chat_session()`, and `index.py:reindex()`.

### The Irony

The project already has a **`ServiceRegistry`** and **`ServiceProvider`** pattern explicitly designed to centralize this wiring. However, `register_service()` is **never called in production code** — only in tests. Every real entry point manually constructs the full dependency graph from scratch.

### The Consequences Already Appearing

The copies have already diverged in subtle ways:

1. **Inconsistent comparison style**: `agent.py` compares `config.gateway.value == ModelGateway.OLLAMA` (string vs StrEnum), while all other files compare `config.gateway == ModelGateway.OLLAMA` (enum vs enum). Both work because `StrEnum` handles it, but the inconsistency signals knowledge drift.

2. **Inconsistent error handling**: `agent.py` raises `ValueError` for unknown gateways, while `qt.py`, `cli.py`, `index.py`, and `diagnose.py` silently default to Ollama. `config.py` prints an error and returns an empty list.

3. **Inconsistent feature sets**: `qt.py` constructs only a subset of tools (no memory, no git, no link traversal), while `agent.py` constructs the full set. If a new service is added, you must update 4+ files — and you'll likely miss one.

### How to Correct It

**Extract a single composition root** — a factory that takes a `Config` and returns a fully wired dependency graph. This could either:

1. **Populate the existing `ServiceRegistry`** with a `build_service_registry(config: Config) -> ServiceRegistry` function, giving the existing `ServiceProvider` its purpose in production code, or

2. **Create a simpler factory** that returns a context object with all wired services, if the full registry pattern feels too heavy.

**Extract gateway creation** into a single function (like `index.py`'s `_make_gateway` already attempts locally — but it needs to live in a shared location like `config.py` or a new `factories.py`):

```python
def create_model_gateway(config: Config) -> OllamaGateway | OpenAIGateway:
    match config.gateway:
        case ModelGateway.OLLAMA:
            return OllamaGateway()
        case ModelGateway.OPENAI:
            return OpenAIGateway(os.environ.get("OPENAI_API_KEY"))
```

Then each entry point (`agent`, `qt`, `index`, `cli`, `diagnose`) calls this single function instead of re-implementing the decision.

**The project is otherwise well-structured** — the testing patterns are strong (425 BDD-style specs), the gateway pattern is cleanly applied, and the service boundaries are well-defined. Centralizing the wiring would bring the architectural intent (ServiceRegistry/ServiceProvider already exists!) into alignment with the actual execution paths.