No tracked files changed — all direct dependencies in `pyproject.toml` were already at their latest versions, so only the `.venv/` (untracked) was modified. Nothing to commit.

---

**Summary of dependency update run:**

**Direct dependencies** (`pyproject.toml`) — all already current:
| Package | Version |
|---|---|
| chromadb | 1.5.9 ✅ |
| mojentic | 1.5.0 ✅ |
| pyside6 | 6.11.1 ✅ |
| rich | 15.0.0 ✅ |
| typer | 0.26.7 ✅ |
| fastmcp | 3.4.2 ✅ |
| pyyaml | 6.0.3 ✅ |

**Transitive dependencies upgraded:**
- `anthropic` 0.107.1 → 0.109.1
- `cryptography` 48.0.0 → 48.0.1
- `cyclopts` 4.16.1 → 4.17.0
- `hf-xet` 1.5.0 → 1.5.1
- `tqdm` 4.68.1 → 4.68.2

**Blocked by upstream conflicts (pinned at current version):**
- `huggingface_hub` stays at 1.16.1 — v1.18.0 imposes `typer<0.26.0`, conflicting with our `typer>=0.26.7`
- `protobuf` stays at 6.33.6 — v7.x is blocked by `opentelemetry-proto 1.42.1` which requires `protobuf<7.0`
- `pydantic_core` stays at 2.46.4 — v2.47.0 needs a pydantic release newer than 2.13.4 (which pins the exact core version)

**Quality gates:** lint ✅ · 796 tests ✅