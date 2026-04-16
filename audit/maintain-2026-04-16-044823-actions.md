All dependency updates are complete. Here's a summary of what happened:

## Dependency Update Results

### ✅ Updated (minor/patch — safe)

| Package | Before | After | Type |
|---|---|---|---|
| `authlib` | 1.6.10 | 1.6.11 | patch |
| `openai` | 2.31.0 | 2.32.0 | minor |
| `pydantic` | 2.13.0 | 2.13.1 | patch |
| `pydantic-core` | 2.46.0 | 2.46.1 | patch |

### ⏭️ Skipped (major version bumps or resolver-blocked)

| Package | Current | Latest | Reason |
|---|---|---|---|
| `importlib-metadata` | 8.7.1 | 9.0.0 | Major bump; resolver can't satisfy due to `keyring` and `opentelemetry-api` constraints |
| `protobuf` | 6.33.6 | 7.34.1 | Major bump; constrained by `googleapis-common-protos`, `onnxruntime`, `opentelemetry-proto` |
| `mpmath` | 1.3.0 | 1.4.1 | Constrained by transitive deps — resolver can't satisfy |

All three skipped packages are transitive dependencies not directly declared in `pyproject.toml` — the resolver correctly kept them at compatible versions.

### ✅ Quality Gates

- **Lint** (`ruff check .`): Clean — zero warnings
- **Tests** (`pytest`): All 728 tests passed in 1.72s