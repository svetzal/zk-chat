All three remaining "outdated" entries are intentionally pinned due to upstream conflicts:

| Package | Installed | Latest | Reason held back |
|---|---|---|---|
| `huggingface_hub` | 1.16.1 | 1.19.0 | 1.17+ requires `typer<0.26.0`, conflicts with project's `typer>=0.26.7` |
| `protobuf` | 6.33.6 | 7.35.1 | `opentelemetry-proto 1.42.1` (latest) requires `protobuf<7.0` |
| `pydantic_core` | 2.46.4 | 2.47.0 | `pydantic 2.13.4` (latest) pins exactly `pydantic-core==2.46.4` |

**Successfully upgraded (transitive dependencies):**
- `anthropic` 0.109.1 → 0.109.2
- `anyio` 4.13.0 → 4.14.0
- `filelock` 3.29.3 → 3.29.4
- `fsspec` 2026.4.0 → 2026.6.0
- `mcp` 1.27.2 → 1.28.0
- `onnxruntime` 1.26.0 → 1.27.0
- `openai` 2.41.1 → 2.42.0
- `pytest` 9.0.3 → 9.1.0
- `tqdm` 4.68.2 → 4.68.3

Both quality gates pass: **800 tests ✓, lint clean ✓**.