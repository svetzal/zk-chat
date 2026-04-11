All dependencies in **zk-chat** have been updated successfully. Here's what changed:

## ✅ Dependency Update Complete

All 723 tests pass and ruff reports zero warnings.

### Updated packages
| Package | Change | Type |
|---|---|---|
| chromadb | 1.5.5 → 1.5.7 | Direct dep — patch |
| fastmcp | 3.2.0 → 3.2.3 | Direct dep — patch |
| rich | 14.3.3 → 14.3.4 | Direct dep — patch |
| anthropic | 0.89.0 → 0.94.0 | Transitive — minor |
| openai | 2.30.0 → 2.31.0 | Transitive — minor |
| mcp | 1.26.0 → 1.27.0 | Transitive — minor |
| uvicorn | 0.42.0 → 0.44.0 | Transitive — minor |
| huggingface-hub | 1.8.0 → 1.10.1 | Transitive — minor |
| opentelemetry-* | 1.40.0 → 1.41.0 | Transitive — minor |
| cryptography | 46.0.6 → 46.0.7 | Transitive — security patch |
| ruff | 0.15.8 → 0.15.10 | Dev tool — patch |
| Several others | — | Patch bumps |

### Skipped (constrained by transitive deps)
- **protobuf** — `opentelemetry-proto` caps it below 7.0
- **pydantic-core** — constrained by pydantic's current release
- **importlib-metadata** — capped by opentelemetry-api and keyring

The `uv.lock` file has been updated with the new pinned versions for reproducible builds.