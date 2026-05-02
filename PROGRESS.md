# Project Progress

## Milestones

### ✅ DONE: memory-inbox (capture layer)
- Deterministic Python CLI/library core
- Repeatable scenario evaluator (3 scenarios, all pass)
- Project-local Pi extension adapter
- Redacted adapter trace helper
- Candidate listing helper
- **13 unit tests passing**
- YOLO capture-first policy implemented

**Files**: `memory/memory-inbox/`, `.pi/extensions/memory-inbox/`

### ✅ DONE: Research
- Local agentic memory landscape analysis (16 projects)
- Critical review of current project
- Identified best matches: Ori-Mnemos, zer0dex, Cognee, Remnic
- External repos archived in `research/external-repos/`

**Files**: `research/local-agentic-memory-landscape.md`, `research/memory-system-critical-review.md`

### ✅ DONE: Context Window Probe
- Task spec written
- Identified existing extension `pi-llama-cpp` that solves the problem
- Recommended: install `npm:pi-llama-cpp` or manually set `contextWindow: 141312`

**Files**: `tasks/context-window-probe-extension.md`

### 📋 PLANNED: memory-consolidator Gen1 (storage + retrieval)
- Plan written: `memory/memory-consolidator/PLAN-GEN1.md`
- Scope: candidates → SQLite → FTS5 retrieval
- Anti-goals: no ontology, no vector search, no LLM extraction, no hierarchy
- Migration path: 7 generations planned
- Estimated: 6-7 days

**Files**: `memory/memory-consolidator/PLAN-GEN1.md`

### 🔜 NEXT: memory-consolidator Gen1 Implementation
- Database schema + setup
- Memory dataclass + schema parsing
- SimplePromoter
- Consolidator core
- FTS5 search
- CRUD operations
- Rebuild + health check
- CLI interface
- Pi extension tools
- Tests

## Current Status

| Component | Status | Tests |
|---|---|---|
| memory-inbox | ✅ Implemented | 13 passing |
| memory-consolidator | 📋 Planned (Gen1) | — |
| Pi extension adapter | ✅ Implemented | — |
| Research | ✅ Complete | — |

## Deferred Features (documented in PLAN-GEN1.md)

- Ontology folding / knowledge graph (Gen4+)
- Contradiction detection/resolution (Gen3+)
- Supersession / temporal memory management (Gen3+)
- Multi-backend fan-out (Gen6)
- Hierarchical memory layers (Gen5)
- Semantic vector search (Gen2)
- LLM-based content extraction (Gen2+)
- Background consolidation jobs (Gen3+)
- Memory quality evaluation / golden queries (Gen2+)
- Confidence scoring (Gen3+)
- Activation decay (Gen3+)
- RRF fusion ranking (Gen2+)
- PageRank graph retrieval (Gen4+)
