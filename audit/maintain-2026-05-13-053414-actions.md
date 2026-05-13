All done. Here's a summary of what was updated:

**Direct dependency updated:**
- `mojentic` 1.2.1 → 1.4.0 — confirmed safe: the public API surface used by zk-chat (`mojentic.llm`, `mojentic.llm.gateways`, `mojentic.llm.tools`) is unchanged; the only structural difference is a new roundtrip spec file added in the gateways module.

**Transitive dependencies updated (minor/patch only):**
- `anthropic` 0.100.0 → 0.101.0
- `requests` 2.33.1 → 2.34.0
- `sse-starlette` 3.4.2 → 3.4.4
- `idna` 3.14 → 3.15

**Skipped major version bumps (transitive, higher risk):**
- `importlib_metadata` 8.7.1 → 9.0.0
- `protobuf` 6.33.6 → 7.34.1

Both quality gates passed cleanly: lint (0 warnings) and 767 tests green.