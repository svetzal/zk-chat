All done. Here's a summary of what happened:

**Runtime dependencies** — all 7 were already at their latest versions (chromadb 1.5.9, mojentic 1.5.0, pyside6 6.11.1, rich 15.0.0, typer 0.26.7, fastmcp 3.4.2, pyyaml 6.0.3).

**Dev tooling** — one update:
- `ruff` 0.15.18 → **0.15.19**

**Lock & requirements refresh** — `uv lock --upgrade-package ruff` updated `uv.lock`, and `uv export` regenerated `requirements.txt`, which was stale (still listed fastmcp 3.3.1 and older transitive packages). The refreshed file now correctly pins all the latest resolved transitive versions.

**Quality gates**: 832 tests ✓, lint clean ✓. Committed and pushed to `main`.