The plan is written to `PLAN.md` and ready for your review. Here's a quick summary of the three phases:

**Phase 1 — Inject Services into Tools** (Steps 1.1–1.15): Change all 11 tool constructors from accepting `Zettelkasten` to accepting the specific service they actually use (`DocumentService`, `IndexService`, `LinkTraversalService`, or `MarkdownFilesystemGateway`). Update the wiring in `agent.py`, `qt.py`, and `mcp.py`. Update all corresponding test files.

**Phase 2 — Remove Duplicated Wiring & Migrate Remaining Consumers** (Steps 2.1–2.4): Extract shared tool-wiring logic from the duplicated `agent()` / `agent_single_query()` functions. Migrate `index.py` and `diagnose.py` from `Zettelkasten` to `IndexService`.

**Phase 3 — Retire Zettelkasten** (Steps 3.1–3.5): Remove `Zettelkasten` class, its tests, and its references from the service registry. Verify zero remaining references.

Each phase is independently shippable with tests passing at every step.