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

### ✅ DONE: memory-consolidator Gen1 (storage + retrieval)
- SQLite database with FTS5 full-text search index + triggers
- Memory dataclass with from_row/to_dict serialization
- SimplePromoter: candidate → memory with provenance
- Consolidator core: promote, reject, merge, search, CRUD, rebuild, health check
- CLI interface (promote, search, list, get, archive, rebuild, health)
- Pi extension adapter with 4 tools
- **27 unit tests passing**

**Files**: `memory/memory-consolidator/src/`, `.pi/extensions/memory-consolidator/`

### 🔜 NEXT: memory-consolidator Gen2 (semantic search)
- Add ONNX local embeddings
- Vector index (SQLite or separate store)
- Hybrid BM25 + vector ranking
- Confidence scoring
- Golden query evaluation

## Current Status

| Component | Status | Tests |
|---|---|---|
| memory-inbox | ✅ Implemented | 13 passing |
| memory-consolidator Gen1 | ✅ Implemented | 27 passing |
| Pi extension adapter (inbox) | ✅ Implemented | — |
| Pi extension adapter (consolidator) | ✅ Implemented | — |
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
