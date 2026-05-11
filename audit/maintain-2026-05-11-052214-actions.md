All 767 tests pass. Here's a summary of what was updated:

**Updates applied:**
- `coverage` 7.13.5 → 7.14.0 (patch)
- `idna` 3.13 → 3.14 (minor)
- `mcp` 1.27.0 → 1.27.1 (patch — transitive dep of `fastmcp`)
- `pydantic-settings` 2.14.0 → 2.14.1 (patch)
- `python-multipart` 0.0.27 → 0.0.28 (patch)
- `regex` 2026.4.4 → 2026.5.9 (patch)
- `onnxruntime` 1.25.1 → 1.26.0 (minor — transitive dep of `chromadb`)

**Skipped (dependency conflicts):**
- `importlib_metadata` 9.0.0 — blocked by `opentelemetry-api 1.41.1` which requires `<8.8.0`
- `protobuf` 7.x — blocked by `opentelemetry-proto 1.41.1` which requires `<7.0`

Both blockages originate from `chromadb`'s pinned OpenTelemetry dependencies. They'll unblock when `chromadb` releases a version with updated OpenTelemetry constraints.

All direct project dependencies (`chromadb`, `mojentic`, `fastmcp`, `typer`, `rich`, `pyyaml`, `pyside6`) were already at their latest versions. Lint and tests pass cleanly.