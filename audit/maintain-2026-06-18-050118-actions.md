All 800 tests pass and lint is clean. Here's a summary of what happened:

**Successfully updated:**
- `certifi` 2026.5.20 → 2026.6.17 ✅
- `cyclonedx-python-lib` 11.10.0 → 11.11.0 ✅
- `openai` 2.42.0 → 2.43.0 ✅

**Reverted due to dependency conflicts:**
- `huggingface_hub` — 1.19.0 requires `typer<0.26.0`, but the project needs `typer>=0.26.7`
- `protobuf` — 7.35.1 is incompatible with `opentelemetry-proto 1.42.1` which requires `protobuf<7.0`
- `pydantic_core` — 2.47.0 is not compatible with the current latest `pydantic 2.13.4` which pins `pydantic-core==2.46.4`

The three packages that remain "outdated" are all **blocked by transitive dependency constraints** — they can't be upgraded until their upstream packages (huggingface_hub's typer pin, opentelemetry-proto's protobuf ceiling, and pydantic's exact pydantic-core pin) are relaxed in their own newer releases.