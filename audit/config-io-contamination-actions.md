All 10 steps of the architectural improvement are complete. Here's the final status:

## Summary

The **Functional Core / Imperative Shell** refactoring of the configuration layer is fully implemented and verified.

### Quality Gates ✅
- **264 tests pass** (37 more than before the refactoring)
- **Zero lint warnings** (`ruff check zk_chat` — all checks passed)
- **Coverage improvements**: `config.py` 100%, `config_gateway.py` 100%, `global_config.py` 96%, `global_config_gateway.py` 100%

### What Was Done
1. **`ConfigGateway`** — thin I/O wrapper handling vault config persistence (`load()` / `save()`)
2. **`GlobalConfigGateway`** — thin I/O wrapper for global bookmarks/MCP config, with injectable `config_path` for testability
3. **`Config`** — now a pure Pydantic data model with zero file I/O; 100% covered by tests
4. **`GlobalConfig`** — now a pure Pydantic data model; mutation methods no longer auto-save; callers explicitly save via gateway
5. **`model_selection.py`** — extracted interactive `input()`/`print()` model-selection logic into the imperative shell
6. **Service registry** — `CONFIG_GATEWAY` and `GLOBAL_CONFIG_GATEWAY` registered as services
7. **All callers migrated** — `cli.py`, `index.py`, `qt.py`, `agent.py`, `mcp_client.py`, `mcp_tool_wrapper.py`, all `commands/` and `upgraders/` updated to use gateways explicitly
8. **Deprecated I/O methods removed** — `Config.load()`, `Config.save()`, `Config.load_or_initialize()`, `Config.update_model()`, `GlobalConfig.load()`, `GlobalConfig.save()` all gone