No project files needed updating — this project uses lower-bound constraints in `pyproject.toml` without a lockfile, so all updates were applied directly to the virtual environment.

**Summary of dependency updates:**

| Package | Before | After | Notes |
|---|---|---|---|
| `anthropic` | 0.115.1 | 0.116.0 | ✅ Upgraded (transitive) |
| `coverage` | 7.14.3 | 7.15.0 | ✅ Upgraded (dev transitive) |
| `filelock` | 3.29.4 | 3.29.5 | ✅ Upgraded (transitive) |
| `pymdown-extensions` | 11.0 | 11.0.1 | ✅ Upgraded (dev dep) |
| `typing_extensions` | 4.15.0 | 4.16.0 | ✅ Upgraded (transitive) |
| `huggingface_hub` | 1.16.1 | 1.21.0 ❌ | Blocked — 1.16.4+ requires `typer<0.26.0`, conflicts with `zk-chat`'s `typer>=0.26.8` |
| `pydantic_core` | 2.46.4 | 2.47.0 ❌ | Blocked — pinned exactly by `pydantic` 2.13.4 (the latest pydantic) |

**Quality gates:** ✅ lint (0 warnings), ✅ tests (832 passed), ✅ audit (no vulnerabilities)