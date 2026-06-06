All done. Here's a summary of what happened:

**Updated (installed + pyproject.toml):**
- `fastmcp` 3.4.0 → 3.4.2 (patch; lower bound bumped in `pyproject.toml`)

**Updated in venv only (transitive deps):**
- `anthropic` 0.105.2 → 0.106.0
- `structlog` 25.5.0 → 26.1.0 (CalVer — year-based versioning, not a true major bump)
- `tqdm` 4.67.3 → 4.68.1

**Intentionally left at current versions:**
- `huggingface-hub` — 1.17+ introduces `typer<0.26` which conflicts with the project's `typer>=0.26.7`; stays at 1.16.1
- `protobuf` — major bump (6.x → 7.x), skipped per guidelines
- `pydantic-core` — pinned exactly by `pydantic 2.13.4`; would need a coordinated pydantic upgrade to move

Quality gates: **788 tests passing, zero lint warnings** ✓