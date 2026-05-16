All done. Here's a summary of what was updated:

**Direct dependency updated in `pyproject.toml`:**
- `fastmcp` 3.3.0 → 3.3.1 (patch; minimum constraint bumped to `>=3.3.1,<4.0.0`)

**Transitive dependencies upgraded in the venv (minor/patch, safe):**
- `aiofile` 3.9.0 → 3.11.1
- `fastmcp-slim` 3.3.0 → 3.3.1 (companion to fastmcp)
- `huggingface_hub` 1.14.0 → 1.15.0
- `jaraco.functools` 4.4.0 → 4.5.0
- `numpy` 2.4.4 → 2.4.5
- `openai` 2.36.0 → 2.37.0

**Skipped (major version bumps for transitive deps):**
- `importlib_metadata` 8.7.1 → 9.0.0
- `protobuf` 6.33.6 → 7.34.1
- `rich-rst` 1.3.2 → 2.0.1

All other direct dependencies (chromadb, pyyaml, mojentic, pyside6, rich, typer) were already at their latest versions. Both quality gates passed: lint is clean and all 767 tests pass.