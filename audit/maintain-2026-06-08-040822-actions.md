All direct dependencies were already at their latest versions. Here's a summary of what was done:

**Updated (transitive dependencies in `uv.lock`):**
| Package | Old | New | Type |
|---|---|---|---|
| `aiohttp` | 3.14.0 | 3.14.1 | patch |
| `anthropic` | 0.107.0 | 0.107.1 | patch |
| `cyclonedx-python-lib` | 11.8.0 | 11.9.0 | minor |
| `joserfc` | 1.7.0 | 1.7.1 | patch |

**Not upgraded (dependency constraints):**
- `huggingface_hub` 1.16.1 — constrained by chromadb
- `protobuf` 6.33.6 — major bump (→7.x) blocked by chromadb's upper bound
- `pydantic_core` 2.46.4 — constrained by pydantic

uv resolved these correctly without any intervention needed. Both quality gates pass clean: **788/788 tests** ✓ and **ruff — zero warnings** ✓.