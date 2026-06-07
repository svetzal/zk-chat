Dependencies updated and pushed. Here's a summary of what happened:

**Updates applied (all via `uv lock --upgrade`):**
| Package | Before | After |
|---------|--------|-------|
| anthropic | 0.106.0 | 0.107.0 |
| openai | 2.38.0 | 2.41.0 |
| structlog | 25.5.0 | 26.1.0 |
| aiohttp | 3.13.5 | 3.14.0 |
| uvicorn | 0.48.0 | 0.49.0 |
| ruff | 0.15.15 | 0.15.16 |
| tqdm | 4.67.3 | 4.68.1 |
| kubernetes | 36.0.1 | 36.0.2 |
| python-multipart | 0.0.30 | 0.0.32 |
| filelock | 3.29.0 | 3.29.1 |
| idna | 3.17 | 3.18 |
| joserfc | 1.6.8 | 1.7.0 |
| cyclonedx-python-lib | 11.7.0 | 11.8.0 |

**Held back (resolver constraints):**
- `huggingface-hub` (1.16.1) — locked by `tokenizers 0.23.1` compatibility
- `pydantic-core` (2.46.4) — tightly coupled to `pydantic 2.13.4` (already latest)
- `protobuf` (6.33.6) — `onnxruntime` and `opentelemetry` constrain it to `<7`

All 788 tests pass, lint is clean.