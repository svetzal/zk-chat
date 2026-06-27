All quality gates pass. Here's the summary of the dependency update run:

**All direct dependencies are already at their latest compatible versions:**

| Package | Installed | Latest |
|---------|-----------|--------|
| chromadb | 1.5.9 | 1.5.9 ✓ |
| fastmcp | 3.4.2 | 3.4.2 ✓ |
| mojentic | 1.5.0 | 1.5.0 ✓ |
| pyside6 | 6.11.1 | 6.11.1 ✓ |
| rich | 15.0.0 | 15.0.0 ✓ |
| typer | 0.26.8 | 0.26.8 ✓ |
| pyyaml | 6.0.3 | 6.0.3 ✓ |
| ruff | 0.15.20 | 0.15.20 ✓ |
| pytest | 9.1.1 | 9.1.1 ✓ |

**Two transitive deps show as "outdated" but cannot be updated due to upstream constraint conflicts:**

- `huggingface_hub` (1.16.1 → 1.21.0): Blocked — `huggingface_hub` 1.21.0 requires `typer<0.26.0`, which conflicts with `zk-chat`'s `typer>=0.26.7` requirement. The `huggingface_hub` maintainers need to relax that cap before this can advance.
- `pydantic_core` (2.46.4 → 2.47.0): Blocked — `pydantic 2.13.4` (the current latest) pins `pydantic-core==2.46.4` exactly. The `2.47.0` core release is ahead of any pydantic release that references it.

**Quality gates:** ✅ lint — all checks passed | ✅ tests — 832 passed in 1.22s

No changes needed to `pyproject.toml`; the environment is in the best possible state given current upstream constraints.