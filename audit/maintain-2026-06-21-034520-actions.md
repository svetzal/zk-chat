All done. Here's a summary of what was updated:

**8 packages upgraded** (all patch/minor — no breaking changes):

| Package | Before | After |
|---|---|---|
| anthropic | 0.109.2 | 0.111.0 |
| coverage | 7.14.1 | 7.14.2 |
| griffelib | 2.0.2 | 2.1.0 |
| msgpack | 1.2.0 | 1.2.1 |
| pydantic-settings | 2.14.1 | 2.14.2 |
| pytest | 9.1.0 | 9.1.1 |
| ruff | 0.15.17 | 0.15.18 |
| sse-starlette | 3.4.4 | 3.4.5 |

All direct dependencies in `pyproject.toml` were already at their latest versions. The one outlier from `pip list --outdated` — `protobuf` (6.33.6 → 7.35.1) — was skipped because uv's resolver determined the current version satisfies all constraints; the major jump likely has downstream incompatibilities with chromadb or another transitive dependency.

Quality gates: ✅ lint clean, ✅ 807/807 tests passing. Committed and pushed to `main`.