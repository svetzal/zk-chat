All quality gates pass with the updates applied. Here's a summary of what happened:

**Successfully upgraded (venv-only, no `pyproject.toml` changes needed since constraints use `>=`):**
| Package | Before | After |
|---|---|---|
| `starlette` | 1.3.0 | 1.3.1 (patch) |
| `cryptography` | 48.0.1 | 49.0.0 (major, no breaking changes for this usage) |

**Remaining outdated — blocked by transitive constraints:**
| Package | Current | Latest | Blocked by |
|---|---|---|---|
| `huggingface_hub` | 1.16.1 | 1.19.0 | Requires `typer<0.26.0`, conflicts with our `typer>=0.26.7` |
| `protobuf` | 6.33.6 | 7.35.1 | `opentelemetry-proto` requires `protobuf<7.0` |
| `pydantic_core` | 2.46.4 | 2.47.0 | `pydantic 2.13.4` pins it exactly at 2.46.4 |

These three are all held back by their sibling transitive dependencies — they'll unlock naturally when `chromadb` (which pulls in `huggingface_hub` and `opentelemetry-proto`) and `pydantic` publish new releases with updated constraints.

**Quality gates:** ✅ lint clean, ✅ 796 tests passed.