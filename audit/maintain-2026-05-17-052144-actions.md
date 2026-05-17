Clean — no vulnerabilities found. Here's the full dependency update summary:

**Upgraded successfully:**
| Package | Before | After |
|---|---|---|
| `cachetools` | 7.1.1 | 7.1.2 |
| `click` | 8.3.3 | 8.4.0 |
| `cyclopts` | 4.12.0 | 4.13.0 |

**Skipped (locked by transitive constraints):**
| Package | Available | Blocked by |
|---|---|---|
| `importlib_metadata` | 9.0.0 | `opentelemetry-api` requires `<8.8.0` |
| `protobuf` | 7.34.1 | `opentelemetry-proto` requires `<7.0` |
| `rich-rst` | 2.0.1 | `cyclopts` requires `<2.0.0` |

**Direct project dependencies** (`pyproject.toml`): all already at their latest compatible versions — `chromadb`, `mojentic`, `fastmcp`, `pyside6`, `rich`, `typer`, `pyyaml` are each pinned to the current latest.

Quality gates: ✅ lint clean, ✅ 767 tests pass, ✅ no security vulnerabilities.