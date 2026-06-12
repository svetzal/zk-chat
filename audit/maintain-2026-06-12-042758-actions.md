Dependency update complete. Here's the summary:

**Updated (13 packages in `uv.lock`):**
| Package | Before | After |
|---|---|---|
| anthropic | 0.107.1 | 0.109.1 |
| cryptography | 48.0.0 | 48.0.1 |
| cyclonedx-python-lib | 11.9.0 | 11.10.0 |
| cyclopts | 4.16.1 | 4.18.0 |
| filelock | 3.29.1 | 3.29.3 |
| grpcio | 1.81.0 | 1.81.1 |
| hf-xet | 1.5.0 | 1.5.1 |
| msgpack | 1.1.2 | 1.2.0 |
| openai | 2.41.0 | 2.41.1 |
| pip-audit | 2.10.0 | 2.10.1 |
| ruff | 0.15.16 | 0.15.17 |
| starlette | 1.2.1 | 1.3.0 |
| tqdm | 4.68.1 | 4.68.2 |

**Held back (dependency conflicts):**
- **`huggingface_hub`** — 1.16.4+ added `typer<0.26.0` which conflicts with zk-chat's `typer>=0.26.7`; staying at 1.16.1
- **`pydantic_core 2.47.0`** — requires a pydantic >2.13.4 that isn't released yet
- **`protobuf 7.x`** — major version jump, skipped per policy

**Security note:** `CVE-2026-45829` in chromadb 1.5.9 has no fix available yet. It only affects server-mode with `trust_remote_code=True`, which zk-chat doesn't use (embedded local use only).

Quality gates: ✅ lint clean, ✅ 796 tests passing.