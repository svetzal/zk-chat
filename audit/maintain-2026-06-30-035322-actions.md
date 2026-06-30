All done. Here's a summary of what happened:

**Direct dependencies** — all already at their latest compatible versions (chromadb 1.5.9, mojentic 1.5.0, fastmcp 3.4.2, typer 0.26.8, rich 15.0.0, pyside6 6.11.1, pyyaml 6.0.3).

**Transitive dependencies upgraded:**
| Package | Before | After |
|---|---|---|
| anthropic | 0.112.0 | 0.113.0 |
| cyclopts | 4.19.0 | 4.20.0 |
| jiter | 0.15.0 | 0.16.0 |
| joserfc | 1.7.1 | 1.7.2 |
| regex | 2026.5.9 | 2026.6.28 |
| rpds-py | 2026.5.1 | 2026.6.3 |

**Intentionally skipped:**
- `huggingface_hub` 1.21.0 would have required downgrading typer to <0.26.0, conflicting with our `typer>=0.26.8` direct requirement — left at 1.16.1
- `pydantic_core` 2.47.0 is incompatible with pydantic 2.13.4 (which pins `pydantic-core==2.46.4`); pydantic is already at its latest

**Quality gates:** lint ✓ · 832 tests ✓ · audit ✓ (no vulnerabilities)

**uv.lock** was also synced to match pyproject.toml's `typer>=0.26.8` (the lockfile had a stale `>=0.26.7`).