# Task: Memory Consolidator Gen1 Implementation

## Goal

Implement Generation 1 consolidator: candidates → SQLite storage → FTS5 retrieval.

## Scope

- Read candidates from `memory/candidates/`
- Store as memories in SQLite with FTS5
- Keyword search over accumulated memories
- Provenance preserved (candidate_id, source, timestamps)
- Basic lifecycle (create, read, update, archive)
- Rebuild from candidates
- Health check
- Pi extension tools

## Anti-goals

- No ontology / knowledge graph
- No semantic vector search
- No LLM-based extraction
- No multi-backend fan-out
- No hierarchical memory
- No background jobs
- No memory quality scoring

## Implementation Order

1. Database schema + setup (~1 day)
2. Memory dataclass + schema parsing (~0.5 day)
3. SimplePromoter (~0.5 day)
4. Consolidator core (promote, reject, merge) (~1 day)
5. FTS5 search (~0.5 day)
6. List, get, update, archive (~0.5 day)
7. Rebuild + health check (~0.5 day)
8. CLI interface (~0.5 day)
9. Pi extension tools (~0.5 day)
10. Tests (~1 day)

**Estimated: 6-7 days**

## Acceptance Criteria

- [ ] Database schema created (memories, candidates_processed, memory_events)
- [ ] FTS5 index working with triggers
- [ ] SimplePromoter reads candidates and creates memories
- [ ] Consolidator core: promote, reject, merge
- [ ] FTS5 search returns ranked results
- [ ] List, get, update, archive operations work
- [ ] Rebuild from candidates works
- [ ] Health check detects basic issues
- [ ] Pi extension tools registered
- [ ] Tests pass

## References

- Plan: `memory/memory-consolidator/PLAN-GEN1.md`
- Contract: `memory/docs/inbox-consolidator-contract.md`
- Research: `research/local-agentic-memory-landscape.md`
- Critical review: `research/memory-system-critical-review.md`
