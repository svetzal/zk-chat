Now I have a comprehensive picture. Let me compile the assessment.

```json
{ "severity": 3, "principle": "No Knowledge Duplication", "category": "Simple Design Heuristics" }
```

## Assessment

### Overall Health

The project is in **strong shape** overall. The fundamentals are solid:

- ✅ **217 tests pass** — 87% coverage
- ✅ **Zero ruff warnings** — linting is clean
- ✅ **Gateway pattern** applied consistently for I/O boundaries
- ✅ **BDD-style specs** co-located with implementation
- ✅ **Type-safe mocks** (`Mock(spec=...)`) throughout
- ✅ **Pydantic models** for all data containers
- ✅ **Structured logging** via structlog
- ✅ **Modern Python 3.11+** syntax (union types, type hints)

This is a well-crafted codebase. However, one principle stands out as significantly violated.

---

### Most Violated Principle: **No Knowledge Duplication**

> *"Avoid multiple spots that must change together for the same reason."*

The `Zettelkasten` class (372 lines) contains **near-identical logic** to `DocumentService` (338 lines) + `IndexService` (343 lines). This is not coincidental similarity — it is the *same knowledge expressed twice*, meaning a single business change requires editing two locations.

#### Concrete Duplications

**1. `_merge_metadata()` — 30 lines, character-for-character identical in both `Zettelkasten` and `DocumentService`**

Both classes contain the exact same recursive metadata merging algorithm — identical variable names, identical control flow, identical edge-case handling for `None`, lists, and nested dicts.

**2. Document CRUD — duplicated across `Zettelkasten` and `DocumentService`:**
| Operation | Zettelkasten | DocumentService |
|---|---|---|
| `read_document()` | lines 53-60 | lines 45-69 |
| `create_or_overwrite_document()` / `write_document()` | lines 68-100 | lines 71-112 |
| `delete_document()` | lines 350-371 | lines 114-141 |
| `rename_document()` | lines 334-348 | lines 143-164 |
| `append_to_document()` | lines 318-332 | lines 166-188 |
| `document_exists()` | lines 50-51 | lines 227-241 |

**3. Indexing logic — duplicated across `Zettelkasten` and `IndexService`:**
| Operation | Zettelkasten | IndexService |
|---|---|---|
| `reindex()` / `reindex_all()` | lines 106-131 | lines 78-107 |
| `update_index()` | lines 133-159 | lines 109-140 |
| `query_excerpts()` | lines 167-173 | lines 174-197 |
| `query_documents()` | lines 175-194 | lines 199-225 |
| `_split_document()` | lines 218-229 | lines 260-272 |
| `_create_vector_document_for_storage()` | lines 238-247 | lines 283-293 |

**4. Tools are in a confusing halfway state:**

The tools accept `Zettelkasten` but then immediately construct the services from its internals, using `Zettelkasten` as a service locator:

```python
# ReadZkDocument — imports BOTH, uses Zettelkasten only as a bag of dependencies
class ReadZkDocument(LLMTool):
    def __init__(self, zk: Zettelkasten, ...):
        self.zk = zk
        self.document_service = DocumentService(zk.filesystem_gateway)  # <-- pulls from internals
```

```python
# FindExcerptsRelatedTo — even worse, reaching deep into Zettelkasten's guts
class FindExcerptsRelatedTo(LLMTool):
    def __init__(self, zk: Zettelkasten, ...):
        self.index_service = IndexService(
            tokenizer_gateway=zk.tokenizer_gateway,
            excerpts_db=zk.excerpts_db,
            documents_db=zk.documents_db,
            filesystem_gateway=zk.filesystem_gateway
        )
```

The tools **never call a single method on `Zettelkasten`** — they only use it to extract dependencies for the services they actually use. This means `Zettelkasten` has degraded into an informal service locator, while its duplicated methods go unused by the tool layer.

---

### The Risk

If you need to change how metadata merging works, how documents are read, or how queries filter results, you must change it in **two places** — and there's no compiler or test that would catch a divergence. Today both copies are identical; tomorrow a bug fix applied to one might be missed in the other.

---

### Recommended Correction

**Complete the migration to services. Make `Zettelkasten` a thin facade that delegates to `DocumentService` and `IndexService` — or remove it entirely.**

The approach, in small safe increments:

1. **Phase 1 — Delegate**: Rewrite `Zettelkasten`'s methods to delegate to `DocumentService` and `IndexService` internally, removing all duplicated logic. This is safe because no callers change.

2. **Phase 2 — Inject services into tools**: Change tool constructors to accept `DocumentService` / `IndexService` directly instead of `Zettelkasten`. Update the tool wiring in `agent.py` to provide the services. This eliminates the service-locator anti-pattern.

3. **Phase 3 — Evaluate `Zettelkasten`**: Once tools use services directly, audit remaining `Zettelkasten` consumers (25 files). If all callers can be migrated to use the services, `Zettelkasten` can be retired. If some callers legitimately need a unified facade, keep it as a thin delegator with zero logic of its own.

Each phase can be shipped independently. Tests pass at every step. No speculative work — just removing duplication that already has a cleaner home.