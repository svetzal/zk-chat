All quality gates pass. Here's a summary of what happened:

**Dependency update run — 2026-07-01**

| Package | Before | After | Outcome |
|---|---|---|---|
| `anthropic` | 0.113.0 | **0.115.0** | ✅ Upgraded |
| `huggingface_hub` | 1.16.1 | 1.16.1 | ⛔ Blocked — v1.21.0 requires `typer<0.26.0`, conflicts with this project's `typer>=0.26.8` |
| `pydantic_core` | 2.46.4 | 2.46.4 | ⛔ Blocked — `pydantic 2.13.4` (latest) pins it to exactly `2.46.4`; upgrading pydantic_core alone breaks pydantic |

**Quality gates:**
- ✅ Lint: `ruff check .` — all checks passed
- ✅ Tests: 832 passed in 2.29s
- ✅ Audit: no known vulnerabilities (CVE-2026-45829 ignored per gate config)

The two remaining "outdated" entries are genuinely blocked by transitive constraints and cannot be resolved without upstream changes: `huggingface_hub` needs to relax its typer upper bound, and `pydantic_core` will move in lockstep when a new `pydantic` release ships.