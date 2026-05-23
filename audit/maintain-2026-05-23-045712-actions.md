No tracked files changed — the updates were all to transitive dependencies within `.venv` (which is gitignored), and the `pyproject.toml` minimum-version pins for direct dependencies were already current. Nothing to commit.

Here's a summary of what was done:

---

## Dependency Update Summary

**Direct dependencies** — all already at latest:
| Package | Installed | Latest |
|---------|-----------|--------|
| chromadb | 1.5.9 | 1.5.9 ✓ |
| mojentic | 1.5.0 | 1.5.0 ✓ |
| pyside6 | 6.11.1 | 6.11.1 ✓ |
| rich | 15.0.0 | 15.0.0 ✓ |
| typer | 0.25.1 | 0.25.1 ✓ |
| fastmcp | 3.3.1 | 3.3.1 ✓ |
| pyyaml | 6.0.3 | 6.0.3 ✓ |

**Transitive dependencies upgraded:**
| Package | Before | After |
|---------|--------|-------|
| anthropic | 0.104.0 | 0.104.1 |
| joserfc | 1.6.5 | 1.6.7 |
| more-itertools | 11.0.2 | 11.1.0 |

**Held back (upstream constraint):**
| Package | Current | Available | Blocked by |
|---------|---------|-----------|-----------|
| protobuf | 6.33.6 | 7.35.0 | `opentelemetry-proto==1.42.1` requires `protobuf<7.0` |
| pydantic-core | 2.46.4 | 2.47.0 | `pydantic==2.13.4` requires exactly `pydantic-core==2.46.4` |

**Security audit:** Clean — no vulnerabilities found.

**Quality gates:** ✅ `ruff check` passes, ✅ 767/767 tests pass.