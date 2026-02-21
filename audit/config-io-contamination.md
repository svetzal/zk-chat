```json
{ "severity": 3, "principle": "Functional Core, Imperative Shell", "category": "Architecture" }
```

## Assessment: Functional Core / Imperative Shell Violation in Configuration Layer

### What's Going Well

This project is remarkably well-structured in many respects:

- **227 tests pass**, all lint checks clean — the quality gates are green
- **Gateway pattern** is applied consistently and correctly (`FilesystemGateway`, `ChromaGateway`, `GitGateway`)
- **Mock discipline** is excellent — tests mock only gateway boundaries with `Mock(spec=...)`, never library internals
- **BDD test style** (Describe/should) is followed consistently across 30 spec files
- **Domain models** are pure Pydantic BaseModels with no I/O
- **Services** receive gateways via constructor injection — proper composition

### The Core Violation: `Config` and `GlobalConfig` Are Impure Data Models

The most significant principle violation lives in `config.py` and `global_config.py`. These are **Pydantic BaseModels** — which should be pure value objects — but they contain:

#### `Config` (config.py) — Triple I/O Contamination

| Method | Violation |
|--------|-----------|
| `load()` / `save()` | File I/O (`open()`, `os.path.exists()`) |
| `load_or_initialize()` | File I/O **+ interactive console** (`input()`, `print()`) |
| `update_model()` | Console I/O + file I/O + network I/O (via `get_available_models()`) |
| `select_model()` (module fn) | Interactive `input()` loop with `print()` |
| `get_available_models()` (module fn) | Instantiates gateway, calls external service |

The `load_or_initialize()` method is the worst offender — it's a `@classmethod` on a data model that calls `input()` to ask the user to pick a model, `print()` to display options, and `save()` to write to disk. That's **three layers of I/O** fused into a value type.

#### `GlobalConfig` (global_config.py) — Implicit Side Effects

Every mutation method auto-calls `self.save()`, creating hidden I/O side effects:

```python
def add_bookmark(self, vault_path: str) -> None:
    abs_path = os.path.abspath(vault_path)
    self.bookmarks.add(abs_path)
    self.save()  # Surprise! File write on every mutation
```

`add_bookmark()`, `remove_bookmark()`, `set_last_opened_bookmark()`, `add_mcp_server()`, and `remove_mcp_server()` all silently write to `~/.zk_chat`. A caller adding 5 bookmarks triggers 5 file writes with no way to batch or suppress them.

### Why This Matters

1. **Untestability**: `config.py` has **0% test coverage** — it's nearly impossible to unit test because every interesting method requires mocking `input()`, `print()`, `open()`, and `os.path.exists()` simultaneously. The I/O contamination is the direct cause of the coverage gap.

2. **Context rigidity**: The interactive `input()`/`print()` calls in `Config` assume a CLI context. The Qt GUI (`qt.py`) presumably can't use `load_or_initialize()` because it would block the UI thread with `input()`. This likely forces the GUI to duplicate or work around the config logic.

3. **Hidden coupling**: `get_available_models()` does a lazy `from zk_chat.gateway_factory import create_model_gateway` inside the function body — runtime import to avoid circular dependencies, which is a symptom of the data model reaching too far into the service layer.

4. **Implicit side effects**: `GlobalConfig`'s auto-save on mutation means callers can't perform atomic multi-step operations. There's no way to add a bookmark and set it as last-opened without two separate file writes.

### How to Correct It

Separate each config class into three concerns:

**1. Pure data models** (functional core — keep in config models):
```python
class Config(BaseModel):
    """Pure configuration data. No I/O."""
    model_config = ConfigDict(frozen=True)
    vault: str
    model: str
    visual_model: str | None = None
    gateway: ModelGateway = ModelGateway.OLLAMA
    # ... pure methods like get_last_indexed(), set_last_indexed() ...
```

**2. A `ConfigGateway`** (I/O boundary — new gateway class):
```python
class ConfigGateway:
    """Handles config persistence. Thin I/O wrapper."""
    def load(self, vault_path: str) -> Config | None: ...
    def save(self, config: Config) -> None: ...

class GlobalConfigGateway:
    def load(self) -> GlobalConfig: ...
    def save(self, config: GlobalConfig) -> None: ...
```

**3. Interactive selection** (imperative shell — move to CLI commands):
Move `select_model()`, `load_or_initialize()`, and `update_model()` to the CLI layer where `input()`/`print()` belong. The Qt GUI can then implement its own selection UI against the same pure `Config` model.

This separation would:
- Make `Config` and `GlobalConfig` testable as pure data (enabling the missing coverage)
- Allow the Qt GUI to use different I/O for model selection
- Enable batched operations on `GlobalConfig` without N file writes
- Eliminate the hidden circular import in `get_available_models()`
- Follow the same gateway pattern already used successfully everywhere else in the project