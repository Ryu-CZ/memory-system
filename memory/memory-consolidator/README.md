# Memory Consolidator

`memory-consolidator` is the downstream consolidation layer for the memory workspace. **Generation 1 is planned** — see [`PLAN-GEN1.md`](PLAN-GEN1.md).

## Purpose

Consume candidate Markdown records from `memory/candidates/`, store them in a durable backend, and support retrieval over accumulated memories.

## Inputs

- Candidate Markdown records from `memory-inbox`.
- Existing stored memories.

## Outputs

- Stored memories in SQLite (Gen1).
- Keyword retrieval via FTS5 (Gen1).
- Provenance preserved for every memory.

## Non-goals (Gen1)

- No raw capture user experience.
- No promotion of real secrets, credentials, or tokens into active durable memory.
- No ontology folding, knowledge graph, or contradiction detection.
- No semantic vector search.
- No LLM-based content extraction.
- No multi-backend fan-out.
- No hierarchical memory layers.
- No background consolidation jobs.
- No memory quality scoring.

See [`PLAN-GEN1.md`](PLAN-GEN1.md) for full scope and anti-goals.

## Implementation

- **Language**: Python
- **Backend**: SQLite with FTS5
- **Schema**: [`PLAN-GEN1.md`](PLAN-GEN1.md) — detailed schema with level, provenance, and event logging
- **Migration path**: 7 generations planned (Gen1 → Gen7)

## Next Steps

1. Database schema + setup
2. Memory dataclass + schema parsing
3. SimplePromoter
4. Consolidator core (promote, reject, merge)
5. FTS5 search
6. CRUD operations
7. Rebuild + health check
8. CLI interface
9. Pi extension tools
10. Tests

Estimated: 6-7 days.
