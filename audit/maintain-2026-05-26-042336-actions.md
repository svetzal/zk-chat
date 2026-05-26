All dependencies are now up to date. Here's the summary:

**Updated (21 transitive packages):**
- `anthropic` 0.103.1 → 0.104.1
- `cachetools` 7.1.3 → 7.1.4
- `click` 8.4.0 → 8.4.1
- `cyclopts` 4.15.0 → 4.16.1
- `httptools` 0.7.1 → 0.8.0
- `huggingface-hub` 1.16.0 → 1.16.1
- `idna` 3.15 → 3.16
- `joserfc` 1.6.5 → 1.6.7
- `mojentic` 1.4.0 → 1.5.0 *(notable — project's LLM abstraction layer)*
- `more-itertools` 11.0.2 → 11.1.0
- `openai` 2.37.0 → 2.38.0
- `opentelemetry-*` packages 1.42.0 → 1.42.1
- `pyjwt` 2.12.1 → 2.13.0
- `ruff` 0.15.13 → 0.15.14
- `starlette` 1.0.0 → 1.1.0
- `uvicorn` 0.47.0 → 0.48.0

**Intentionally pinned (constraint-bound):**
- `protobuf` stays at 6.33.6 — `opentelemetry-proto` requires `protobuf<7.0`
- `pydantic-core` stays at 2.46.4 — `pydantic==2.13.4` pins it exactly

All direct dependencies were already at their latest versions. Quality gates pass: **lint ✓** (zero warnings), **tests ✓** (775 passed).