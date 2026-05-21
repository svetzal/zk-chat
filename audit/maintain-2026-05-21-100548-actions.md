All 767 tests pass. Both quality gates are green. Here's a summary of what was done:

**Updated transitive dependencies:**
| Package | Before | After | Type |
|---------|--------|-------|------|
| `certifi` | 2026.4.22 | 2026.5.20 | patch (cert store refresh) |
| `huggingface_hub` | 1.15.0 | 1.16.0 | minor |
| `kubernetes` | 35.0.0 | 36.0.0 | major (safe — chromadb only requires `>=28.1.0`) |
| `cyclopts` | 4.14.1 | 4.15.0 | minor |

**Skipped:**
| Package | Reason |
|---------|--------|
| `protobuf` 6.33.6 → 7.35.0 | Blocked by `opentelemetry-proto` which requires `protobuf<7.0` — correct constraint to respect |

**Direct dependencies** were already all at their latest versions (`chromadb`, `pyyaml`, `mojentic`, `pyside6`, `rich`, `typer`, `fastmcp`), so no changes to `pyproject.toml` were needed.