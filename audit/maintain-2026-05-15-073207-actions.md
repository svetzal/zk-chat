All dependency updates are complete and pushed. Here's a summary of what changed:

**Direct dependencies updated in pyproject.toml:**
- `fastmcp` 3.2.4 → 3.3.0 (now split into `fastmcp` + `fastmcp-slim`)
- `pyside6` 6.11.0 → 6.11.1

**Transitive dependencies updated via lock file:**
- `anthropic` 0.100.0 → 0.102.0
- `cyclopts` 4.11.2 → 4.12.0
- `requests` 2.33.1 → 2.34.2
- `tiktoken` 0.12.0 → 0.13.0
- `uvicorn` 0.46.0 → 0.47.0
- `ruff` 0.15.12 → 0.15.13
- `pymdown-extensions` 10.21.2 → 10.21.3
- `mcp` 1.27.0 → 1.27.1, `onnxruntime` 1.25.1 → 1.26.0, `sse-starlette` 3.4.2 → 3.4.4

**Held back** (constrained by dependents): `importlib-metadata` (8→9 major) and `protobuf` (6→7 major) — uv's constraint resolution keeps these pinned at their current compatible versions.

All 767 tests pass and lint is clean ✓