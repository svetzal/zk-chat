Dependencies are up to date. Here's a summary of what changed:

**Updated transitive/dev packages:**
| Package | Before | After |
|---|---|---|
| `coverage` | 7.14.2 | 7.14.3 |
| `cyclopts` | 4.18.0 | 4.19.0 |
| `pymdown-extensions` | 10.21.3 | 11.0 |

**Direct dependencies** (`chromadb`, `pyyaml`, `mojentic`, `pyside6`, `rich`, `typer`, `fastmcp`) were already at their latest versions — no changes needed.

The `protobuf` 6→7 and `huggingface_hub` updates weren't needed as they're constrained by direct dependencies at their current versions. Both quality gates — lint (`ruff check`) and tests (823/823 passed) — are clean. Changes pushed to `origin/main`.