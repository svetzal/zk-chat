Now I have a thorough understanding of the codebase. Here is the complete plan:

---

## Plan: Separate Config Layer into Functional Core / Imperative Shell

### Problem Summary

`Config` and `GlobalConfig` are Pydantic BaseModels (data objects) contaminated with I/O: file reads/writes, interactive `input()`/`print()` calls, and network calls. This makes them untestable (0% coverage on `config.py`), context-rigid (CLI-only), and violates the gateway pattern used everywhere else in the project.

### Guiding Principles

- Follow the same gateway pattern already established (`FilesystemGateway`, `ChromaGateway`, `GitGateway`)
- Pure data models in the core, thin I/O wrappers at the boundary
- Interactive selection logic belongs in CLI commands, not data models
- Each step should leave the tests green

---

### Step 1: Create `ConfigGateway` for vault config persistence

**Goal**: Extract `Config.load()` and `Config.save()` into a new gateway class.

**File to create**: `zk_chat/config_gateway.py`

```python
class ConfigGateway:
    """Thin I/O wrapper for vault config persistence."""

    def load(self, vault_path: str) -> Config | None:
        """Load config from .zk_chat file in the vault, or return None."""
        config_path = os.path.join(vault_path, ".zk_chat")
        if os.path.exists(config_path):
            with open(config_path) as f:
                return Config.model_validate_json(f.read())
        return None

    def save(self, config: Config) -> None:
        """Write config to .zk_chat file in the vault."""
        config_path = os.path.join(config.vault, ".zk_chat")
        with open(config_path, 'w') as f:
            f.write(config.model_dump_json(indent=2))
```

**File to create**: `zk_chat/config_gateway_spec.py`

Write BDD-style tests using a real temp directory (this is a gateway — test the actual I/O, don't mock it):
- `should_return_none_when_no_config_file_exists`
- `should_load_config_from_existing_file`
- `should_save_config_to_file`
- `should_round_trip_config_through_save_and_load`

**Do NOT delete** `Config.load()` or `Config.save()` yet. They will be removed in a later step after all callers are migrated.

---

### Step 2: Create `GlobalConfigGateway` for global config persistence

**Goal**: Extract `GlobalConfig.load()` and `GlobalConfig.save()` into a new gateway class.

**File to create**: `zk_chat/global_config_gateway.py`

```python
class GlobalConfigGateway:
    """Thin I/O wrapper for global config persistence (~/.zk_chat)."""

    def __init__(self, config_path: str | None = None):
        self._config_path = config_path or os.path.expanduser("~/.zk_chat")

    def load(self) -> GlobalConfig:
        """Load global config from disk, or return a fresh default."""
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path) as f:
                    return GlobalConfig.model_validate_json(f.read())
            except Exception:
                return GlobalConfig()
        return GlobalConfig()

    def save(self, config: GlobalConfig) -> None:
        """Write global config to disk."""
        with open(self._config_path, 'w') as f:
            f.write(config.model_dump_json(indent=2))
```

The constructor-injectable `config_path` enables testing with a temp file without patching `os.path.expanduser`.

**File to create**: `zk_chat/global_config_gateway_spec.py`

Write BDD-style tests:
- `should_return_default_config_when_no_file_exists`
- `should_load_config_from_existing_file`
- `should_save_config_to_file`
- `should_return_default_config_when_file_is_corrupt`
- `should_round_trip_config_through_save_and_load`

---

### Step 3: Make `Config` a pure data model

**File to modify**: `zk_chat/config.py`

Remove the following methods from the `Config` class:
- `load()` — moved to `ConfigGateway`
- `save()` — moved to `ConfigGateway`
- `load_or_initialize()` — interactive logic moves to CLI (Step 6)
- `update_model()` — interactive logic moves to CLI (Step 6)

Remove the following module-level functions from `config.py`:
- `get_available_models()` — moves to a new location (Step 5)
- `select_model()` — moves to CLI layer (Step 5)
- `get_config_path()` — inlined into `ConfigGateway`

What remains in `Config`:
- All fields (`vault`, `model`, `visual_model`, `gateway`, `chunk_size`, `chunk_overlap`, `last_indexed`, `gateway_last_indexed`)
- `get_last_indexed()` — pure logic, no I/O
- `set_last_indexed()` — pure mutation, no I/O
- `ModelGateway` enum stays in `config.py` (it's a pure data type)

**File to create**: `zk_chat/config_spec.py`

Write BDD-style tests for the pure `Config` model:
- `should_instantiate_with_required_fields`
- `should_default_gateway_to_ollama`
- `should_get_last_indexed_for_current_gateway`
- `should_get_last_indexed_falling_back_to_deprecated_field`
- `should_set_last_indexed_for_current_gateway`
- `should_set_last_indexed_for_specified_gateway`

---

### Step 4: Make `GlobalConfig` a pure data model

**File to modify**: `zk_chat/global_config.py`

Remove the following methods:
- `load()` — moved to `GlobalConfigGateway`
- `save()` — moved to `GlobalConfigGateway`

Remove the implicit `self.save()` calls from ALL mutation methods. The mutation methods become pure data operations:

- `add_bookmark()` — remove `self.save()`, keep the `os.path.abspath()` call (or better: accept the already-resolved path and let the caller do `os.path.abspath`)
- `remove_bookmark()` — remove `self.save()`
- `set_last_opened_bookmark()` — remove `self.save()`
- `add_mcp_server()` — remove `self.save()`
- `remove_mcp_server()` — remove `self.save()`

**Decision on `os.path.abspath()`**: The `add_bookmark`, `remove_bookmark`, `get_bookmark`, and `set_last_opened_bookmark` methods call `os.path.abspath()`. This is a pure path computation (no I/O) — it resolves relative paths using `os.getcwd()` but doesn't touch the filesystem. Keep this in the model for now for backward compatibility, but consider moving it to the caller layer in a future cleanup.

Remove `get_global_config_path()` module-level function — inlined into `GlobalConfigGateway`.

**File to update**: `zk_chat/global_config_mcp_spec.py`

Update the existing MCP tests:
- Remove all `with patch('zk_chat.global_config.GlobalConfig.save'):` wrappers — they're no longer needed since `save()` is gone from the model
- Tests become simpler and cleaner

**File to create or extend**: `zk_chat/global_config_spec.py`

Write BDD-style tests for the pure `GlobalConfig` model:
- `should_add_bookmark`
- `should_remove_bookmark`
- `should_return_false_when_removing_nonexistent_bookmark`
- `should_clear_last_opened_when_removing_its_bookmark`
- `should_set_last_opened_bookmark`
- `should_return_false_when_setting_last_opened_to_non_bookmark`
- `should_get_last_opened_bookmark_path`
- `should_return_none_when_no_last_opened`

None of these tests need mocking or patching — they're pure data operations.

---

### Step 5: Extract model selection logic into a dedicated module

**Goal**: Move interactive model selection out of `config.py` into a CLI-appropriate location.

**File to create**: `zk_chat/model_selection.py`

Move these functions here:
- `get_available_models(gateway)` — but refactor to accept a gateway factory function or the model gateway instance instead of doing the lazy import itself
- `select_model(gateway, is_visual)` — interactive CLI function using `input()`/`print()`

Refactor `get_available_models()` to eliminate the hidden circular import:

```python
def get_available_models(gateway: ModelGateway) -> list[str]:
    """Fetch available models from the specified gateway.
    
    Parameters
    ----------
    gateway : ModelGateway
        The gateway type to query.
    
    Returns
    -------
    list[str]
        List of available model names.
    """
    from zk_chat.gateway_factory import create_model_gateway
    
    if gateway == ModelGateway.OPENAI and not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        return []
    try:
        g = create_model_gateway(gateway)
    except ValueError as e:
        print(f"Error: {e}")
        return []
    return g.get_available_models()
```

Note: The lazy import from `gateway_factory` still exists here. This is acceptable for now — the key improvement is that this I/O-heavy code is no longer embedded in a data model. A future step could inject the gateway factory, but that's a separate concern.

**No spec file needed** for this module — these functions are imperative shell (interactive I/O). They're not worth unit testing since they're thin wrappers around `input()` and `print()`.

---

### Step 6: Register gateways in the service registry

**File to modify**: `zk_chat/services/service_registry.py`

Add two new `ServiceType` entries:

```python
CONFIG_GATEWAY = "config_gateway"
GLOBAL_CONFIG_GATEWAY = "global_config_gateway"
```

**File to modify**: `zk_chat/services/service_provider.py`

Add two new accessor methods:

```python
def get_config_gateway(self):
    """Get the config gateway for vault config persistence."""
    from zk_chat.config_gateway import ConfigGateway
    return self._registry.get_service(ServiceType.CONFIG_GATEWAY, ConfigGateway)

def get_global_config_gateway(self):
    """Get the global config gateway for global config persistence."""
    from zk_chat.global_config_gateway import GlobalConfigGateway
    return self._registry.get_service(ServiceType.GLOBAL_CONFIG_GATEWAY, GlobalConfigGateway)
```

**File to modify**: `zk_chat/service_factory.py`

Add gateway instantiation and registration in `build_service_registry()`:

```python
from zk_chat.config_gateway import ConfigGateway
from zk_chat.global_config_gateway import GlobalConfigGateway

config_gateway = ConfigGateway()
registry.register_service(ServiceType.CONFIG_GATEWAY, config_gateway)

global_config_gateway = GlobalConfigGateway()
registry.register_service(ServiceType.GLOBAL_CONFIG_GATEWAY, global_config_gateway)
```

---

### Step 7: Migrate all callers of `Config.load()` and `Config.save()`

Each caller that currently uses `Config.load(vault_path)` or `config.save()` must be updated to use `ConfigGateway`. Work through each file:

**`zk_chat/cli.py`**:
- Create a `ConfigGateway()` instance at the top of `common_init()`
- Replace `Config.load(vault_path)` → `config_gateway.load(vault_path)`
- The `_initialize_config()` function currently calls `Config.load_or_initialize()` — rewrite it inline:
  - Use `config_gateway.load(vault_path)`
  - If no config exists, construct a `Config(...)` with the resolved model/gateway
  - Call `config_gateway.save(config)` after construction
  - Move the interactive `select_model()` calls that were in `load_or_initialize()` into this CLI function
- `_maybe_update_models()` calls `config.update_model()` — rewrite inline using `select_model()` from `model_selection.py` and `config_gateway.save(config)`

**`zk_chat/index.py`**:
- In `reindex()` (line 89): replace `config.save()` → accept a `config_gateway` parameter or create one locally, then call `config_gateway.save(config)`
- In `main()` (line 117-125): replace `Config.load()` → `config_gateway.load()`, replace `Config.load_or_initialize()` → inline construction, replace `config.save()` → `config_gateway.save(config)`

**`zk_chat/qt.py`** (lines 280-296):
- In `save_settings()`: replace `Config.load(new_vault_path)` → `config_gateway.load(new_vault_path)`, replace `config.save()` → `config_gateway.save(self.config)`
- In `MainWindow.__init__()`: replace `Config.load(vault_path)` → `config_gateway.load(vault_path)`
- The call to `Config.load_or_initialize()` in `qt.py` should be replaced with: load, and if None, construct a `Config(...)` with defaults chosen via the Qt UI (not `input()`)

**`zk_chat/commands/diagnose.py`**:
- Replace `Config.load(vault_path)` → `config_gateway.load(vault_path)` in `_load_config()`

**`zk_chat/commands/index.py`**:
- Replace `Config.load(vault_path)` → `config_gateway.load(vault_path)` in `_load_config_status()`

**`zk_chat/upgraders/gateway_specific_last_indexed.py`**:
- The `run()` method calls `self.config.save()` — change the upgrader to accept a `ConfigGateway` as a constructor parameter, then call `self.config_gateway.save(self.config)` instead
- Update `_run_upgraders()` in `cli.py` to pass the gateway

---

### Step 8: Migrate all callers of `GlobalConfig.load()` and implicit `save()` calls

Each caller that currently uses `GlobalConfig.load()` must be updated. The mutation methods no longer auto-save, so callers must explicitly call `global_config_gateway.save(global_config)` after mutations.

**`zk_chat/cli.py`**:
- In `common_init()`: create `GlobalConfigGateway()`, replace `GlobalConfig.load()` → `global_config_gateway.load()`
- In `_handle_save()`: after `global_config.add_bookmark()` and `set_last_opened_bookmark()`, add a single `global_config_gateway.save(global_config)` call (batching two operations into one write!)
- In `_handle_remove_bookmark()`: add `global_config_gateway.save(global_config)` after successful removal
- In `_resolve_vault_path()`: add save after `set_last_opened_bookmark()`

**`zk_chat/commands/bookmarks.py`**:
- In `list()`: replace `GlobalConfig.load()` → `GlobalConfigGateway().load()`
- In `remove()`: replace `GlobalConfig.load()` → `gateway.load()`, add `gateway.save(global_config)` after `remove_bookmark()`

**`zk_chat/commands/mcp.py`**:
- In `_register_server()`: replace `GlobalConfig.load()` → `gateway.load()`, add `gateway.save()` after `add_mcp_server()`
- In all other functions that call `GlobalConfig.load()`: use gateway

**`zk_chat/agent.py`**:
- Replace `GlobalConfig.load()` → `GlobalConfigGateway().load()`

**`zk_chat/mcp_tool_wrapper.py`**:
- Replace `GlobalConfig.load()` → `GlobalConfigGateway().load()`

**`zk_chat/mcp_client.py`**:
- Replace `GlobalConfig.load()` → `GlobalConfigGateway().load()`

**`zk_chat/qt.py`**:
- In `save_settings()`: replace `GlobalConfig.load()` → `gateway.load()`, add explicit `gateway.save()` after mutations
- In `MainWindow.__init__()`: same pattern

---

### Step 9: Clean up deprecated methods

**File to modify**: `zk_chat/config.py`

Now that all callers have been migrated, remove:
- `Config.load()` classmethod
- `Config.save()` method
- `Config.load_or_initialize()` classmethod
- `Config.update_model()` method
- `get_config_path()` module-level function
- `get_available_models()` module-level function
- `select_model()` module-level function
- All associated imports (`os`, `Optional`, etc. that are no longer needed)

**File to modify**: `zk_chat/global_config.py`

Remove:
- `GlobalConfig.load()` classmethod
- `GlobalConfig.save()` method
- `get_global_config_path()` module-level function
- All `self.save()` calls (already done in Step 4, but verify none snuck back in)
- Remove `os` import if no longer needed

---

### Step 10: Run quality gates and verify

Run the full quality suite to confirm everything is clean:

1. **Tests**: `pytest` — all tests must pass
2. **Lint**: `ruff check zk_chat` — zero warnings
3. **Format**: `ruff format zk_chat` — consistent formatting
4. **Coverage**: `pytest --cov` — verify `config.py` and `global_config.py` now have meaningful coverage through the new spec files

Check that:
- `config_spec.py` tests all pass (pure data model)
- `global_config_spec.py` tests all pass (pure data model)
- `config_gateway_spec.py` tests all pass (I/O round-trips)
- `global_config_gateway_spec.py` tests all pass (I/O round-trips)
- `global_config_mcp_spec.py` tests still pass (no more mock patches needed)
- All existing 227+ tests still pass

---

### Summary of New Files

| File | Purpose |
|------|---------|
| `zk_chat/config_gateway.py` | Thin I/O wrapper for vault config persistence |
| `zk_chat/config_gateway_spec.py` | Integration tests for ConfigGateway |
| `zk_chat/global_config_gateway.py` | Thin I/O wrapper for global config persistence |
| `zk_chat/global_config_gateway_spec.py` | Integration tests for GlobalConfigGateway |
| `zk_chat/config_spec.py` | Pure unit tests for Config data model |
| `zk_chat/global_config_spec.py` | Pure unit tests for GlobalConfig data model |
| `zk_chat/model_selection.py` | Interactive model selection functions (CLI layer) |

### Summary of Modified Files

| File | Change |
|------|--------|
| `zk_chat/config.py` | Remove all I/O methods, keep pure data + `ModelGateway` enum |
| `zk_chat/global_config.py` | Remove `load()`/`save()`, remove auto-save from mutations |
| `zk_chat/global_config_mcp_spec.py` | Remove `patch('...save')` wrappers |
| `zk_chat/services/service_registry.py` | Add `CONFIG_GATEWAY` and `GLOBAL_CONFIG_GATEWAY` service types |
| `zk_chat/services/service_provider.py` | Add `get_config_gateway()` and `get_global_config_gateway()` |
| `zk_chat/service_factory.py` | Register new gateways |
| `zk_chat/cli.py` | Use gateways, inline interactive config init |
| `zk_chat/index.py` | Use `ConfigGateway` for save/load |
| `zk_chat/qt.py` | Use gateways, remove `load_or_initialize()` dependency |
| `zk_chat/commands/bookmarks.py` | Use `GlobalConfigGateway` |
| `zk_chat/commands/mcp.py` | Use `GlobalConfigGateway` |
| `zk_chat/commands/diagnose.py` | Use `ConfigGateway` |
| `zk_chat/commands/index.py` | Use `ConfigGateway` |
| `zk_chat/agent.py` | Use `GlobalConfigGateway` |
| `zk_chat/mcp_tool_wrapper.py` | Use `GlobalConfigGateway` |
| `zk_chat/mcp_client.py` | Use `GlobalConfigGateway` |
| `zk_chat/upgraders/gateway_specific_last_indexed.py` | Accept `ConfigGateway`, call `gateway.save()` |

### Execution Order

Steps 1–2 can be done in parallel (independent gateways). Steps 3–4 can be done in parallel (independent models). Step 5 depends on Step 3 (needs `select_model` removed from `config.py`). Step 6 depends on Steps 1–2. Steps 7–8 depend on Steps 1–6 (all infrastructure in place). Step 9 depends on Steps 7–8 (all callers migrated). Step 10 runs last.

Recommended safe increments for commits:
1. Steps 1 + 2 → "Add ConfigGateway and GlobalConfigGateway for config persistence"
2. Steps 3 + 4 + 5 → "Make Config and GlobalConfig pure data models"
3. Step 6 → "Register config gateways in service registry"
4. Steps 7 + 8 → "Migrate all callers to use config gateways"
5. Step 9 → "Remove deprecated I/O methods from config models"
6. Step 10 → "Verify quality gates pass"