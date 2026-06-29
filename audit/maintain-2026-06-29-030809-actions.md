All done. Here's a summary of what happened:

**Successfully upgraded:**
- `regex` transitive dependency: `2026.5.9 → 2026.6.28`
- `typer` minimum constraint in `pyproject.toml`: `>=0.26.7 → >=0.26.8` (reflects the installed version)

**Blocked by upstream conflicts:**
- `huggingface_hub 1.21.0` — requires `typer<0.26.0`, which conflicts with our `typer>=0.26.8` requirement. Staying at 1.16.1.
- `pydantic_core 2.47.0` — has no matching released `pydantic` version yet. Staying at 2.46.4 (paired with pydantic 2.13.4).

**Quality gates:** ✅ lint, ✅ 832 tests, ✅ pip-audit (no vulnerabilities, 1 ignored)