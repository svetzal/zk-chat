All done. Here's a summary of what was updated:

**All direct dependencies were already at their latest versions.** The lockfile upgrade pulled in 7 transitive dependency updates:

| Package | Old | New |
|---|---|---|
| `aiohappyeyeballs` | 2.6.2 | 2.7.1 |
| `anthropic` | 0.115.0 | 0.115.1 |
| `cyclopts` | 4.19.0 | 4.20.0 |
| `jiter` | 0.15.0 | 0.16.0 |
| `joserfc` | 1.7.1 | 1.7.2 |
| `regex` | 2026.5.9 | 2026.6.28 |
| `rpds-py` | 2026.5.1 | 2026.6.3 |

All quality gates passed cleanly — **832 tests**, zero lint warnings, no known vulnerabilities. `uv.lock` and `requirements.txt` were regenerated and committed to `main`.