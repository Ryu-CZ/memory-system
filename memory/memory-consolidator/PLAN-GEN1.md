# Memory Consolidator — Generation 1 Plan

**Date**: 2026-05-02  
**Goal**: First working memory system: candidates → storage → retrieval  
**Scope**: Minimal viable consolidator, extensible for future iterations

---

## What Is the Goal

### Primary Goal
Build a **local, durable memory store** that:
1. Accepts candidate text fragments from `memory/candidates/`
2. Stores them with full provenance (source, timestamp, candidate id)
3. Supports keyword retrieval over accumulated memories
4. Is rebuildable from candidates at any time
5. Can grow from dozens to millions of memories without breaking

### Success Criterion
The agent can:
- **Remember**: store a fact/preference/observation
- **Recall**: search for relevant past memories by keyword
- **Preserve**: maintain provenance so every memory traces back to its source
- **Rebuild**: regenerate the entire store from raw candidates if needed

### Why This Matters
Without this, the project is only a capture system with no recall capability.
This generation closes the loop: **capture → store → retrieve**.

---

## What Is NOT in Scope

These are **explicitly deferred** to future iterations:

| Deferred Feature | Reason | Future Gen |
|---|---|---|
| Ontology folding / knowledge graph | Requires entity extraction, relationship modeling | Gen4+ |
| Contradiction detection/resolution | Requires semantic understanding, confidence scoring | Gen3+ |
| Supersession / temporal memory management | Requires belief tracking over time | Gen3+ |
| Multi-backend fan-out | Requires adapter interface, parallel ingestion | Gen6 |
| Hierarchical memory layers | Requires level-based abstraction, driver constraints | Gen5 |
| Semantic vector search | Requires embedding model, vector index | Gen2 |
| LLM-based content extraction | Requires prompt engineering, quality evaluation | Gen2+ |
| Background consolidation jobs | Requires scheduler, incremental processing | Gen3+ |
| Memory quality evaluation / golden queries | Requires test fixtures, regression framework | Gen2+ |
| Confidence scoring | Requires evidence evaluation, decay models | Gen3+ |
| Activation decay | Requires access tracking, decay algorithms | Gen3+ |
| RRF fusion ranking | Requires multiple ranking signals | Gen2+ |
| PageRank graph retrieval | Requires graph structure | Gen4+ |
| Explainable ranking with score breakdown | Requires multiple ranking signals | Gen2+ |

**These are not omissions — they are deliberate deferrals.**
Each can be added iteratively once the foundation works.

---

## What NOT to Do

### ❌ Do NOT implement ontology or knowledge graph in Gen1
- No entity extraction
- No relationship modeling
- No schema inference
- No concept merging
- **Reason**: adds complexity that obscures whether basic retrieval works

### ❌ Do NOT implement semantic vector search in Gen1
- No embedding models
- No vector index
- No similarity search
- **Reason**: FTS5 keyword search is sufficient; vector adds dependency and complexity

### ❌ Do NOT implement LLM-based extraction in Gen1
- No prompt-based content parsing
- No LLM summarization
- No automatic fact extraction
- **Reason**: requires quality evaluation, adds latency, obscures baseline

### ❌ Do NOT implement multi-backend fan-out in Gen1
- No adapter interface
- No parallel storage
- No backend comparison
- **Reason**: single backend proves the concept first

### ❌ Do NOT implement hierarchical memory in Gen1
- No memory levels
- No level-based retrieval
- No cross-level promotion
- **Reason**: requires architectural decisions not yet validated

### ❌ Do NOT make the database the single source of truth
- Database must remain rebuildable from candidates
- No opaque state that cannot be regenerated
- **Reason**: prevents vendor lock-in, enables migration

### ❌ Do NOT add features not in this plan
- No speculative "nice to have" features
- No abstractions for single-use code
- No error handling for impossible scenarios
- **Reason**: keep Gen1 minimal and verifiable

### ❌ Do NOT over-engineer the schema
- SQLite with FTS5 is sufficient
- No migrations framework for Gen1
- No complex triggers or views
- **Reason**: schema will evolve based on real usage

### ❌ Do NOT implement background jobs in Gen1
- No scheduled consolidation
- No periodic re-indexing
- No automatic promotion
- **Reason**: manual control is better for debugging and validation

### ❌ Do NOT implement memory quality scoring in Gen1
- No confidence decay
- No activation tracking
- No freshness scoring
- **Reason**: requires long-term usage data to calibrate

---

## Architecture

```
candidates/ → consolidator → storage backend → retrieval API
```

### Design Principles

1. **Shared bus pattern**: All retrieval paths access the same underlying store
2. **Rebuildability**: Database is always rebuildable from candidates + events
3. **Extensibility**: Schema supports future features without breaking changes
4. **Provenance first**: Every memory traces back to its source candidate
5. **No opaque state**: No derived state that cannot be regenerated
6. **Level预留**: Schema includes level field for future hierarchical abstraction
7. **Event logging**: All changes logged for audit and future analysis
8. **Scoped access**: Memories can be filtered by scope, type, level

### Storage Backend Choice: SQLite

**Why SQLite for Gen1:**
- Zero infrastructure dependency
- Local file-based
- Supports full-text search (FTS5)
- Schema evolution possible
- Rebuildable from candidates
- Can grow to millions of records
- Easy migration to heavier backends later

**Alternatives considered:**
- Pure Markdown files — too slow for retrieval at scale
- ChromaDB — adds dependency, overkill for Gen1
- Neo4j — way too heavy for Gen1
- MemPalace pattern — good inspiration, but we want simpler start

---

## Database Schema

### Table: `memories`

```sql
CREATE TABLE memories (
    id TEXT PRIMARY KEY,              -- promoted memory id
    candidate_id TEXT NOT NULL,       -- source candidate id
    title TEXT NOT NULL,              -- human-readable title
    content TEXT NOT NULL,            -- memory content (text fragment)
    memory_type TEXT NOT NULL,        -- fact, preference, procedure, context, episode, decision
    scope TEXT NOT NULL,              -- project:<path>, global, session:<id>
    level INTEGER DEFAULT 0,          -- abstraction level (0=raw, future use)
    status TEXT NOT NULL DEFAULT 'active',  -- active, archived, superseded
    created_at TEXT NOT NULL,         -- ISO timestamp
    promoted_at TEXT NOT NULL,        -- ISO timestamp when promoted
    source TEXT NOT NULL,             -- user_explicit, observed, inferred, etc.
    source_agent TEXT,                -- main-agent, subagent:<name>, etc.
    sensitivity TEXT DEFAULT 'ordinary',
    retention TEXT DEFAULT 'indefinite',
    tags TEXT,                        -- JSON array of tags
    metadata TEXT,                    -- JSON for extensible metadata
    superseded_by TEXT,               -- id of memory that superseded this
    derived_from TEXT,                -- JSON array of source memory ids
    derived_via TEXT,                 -- how this was derived (manual, auto-merge, etc.)
    confidence REAL DEFAULT 1.0       -- 0.0 to 1.0, how reliable this memory is
);
```

**Design notes:**
- `level` field预留 for future hierarchical abstraction (default 0 = raw)
- `metadata` column allows arbitrary extensions without schema changes
- `derived_from`/`derived_via` preserve provenance for future ontology folding
- `superseded_by` supports future temporal memory management
- All fields support rebuild from candidates + promotion actions

### Table: `candidates_processed`

```sql
CREATE TABLE candidates_processed (
    candidate_id TEXT PRIMARY KEY,
    processed_at TEXT NOT NULL,
    action TEXT NOT NULL,             -- promoted, skipped, merged, rejected
    target_memory_id TEXT,            -- if promoted, which memory
    notes TEXT                        -- why this action was taken
);
```

### Table: `memory_events`

```sql
CREATE TABLE memory_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id TEXT NOT NULL,
    event_type TEXT NOT NULL,         -- created, updated, archived, superseded, merged
    event_at TEXT NOT NULL,
    source_candidate_id TEXT,         -- if from candidate promotion
    source_memory_id TEXT,            -- if from merge/supersession
    metadata TEXT                     -- JSON for event-specific details
);
```

**Design notes:**
- Event log enables full audit trail
- Supports future contradiction detection (see what changed when)
- Supports future activation decay (track access patterns)
- Rebuildable from candidates + actions

### FTS Index

```sql
CREATE VIRTUAL TABLE memories_fts USING fts5(
    title, content, tags, scope, memory_type,
    content=memories,
    content_rowid=id
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER memories_fts_insert AFTER INSERT ON memories
BEGIN
    INSERT INTO memories_fts(rowid, title, content, tags, scope, memory_type)
    VALUES (new.id, new.title, new.content, new.tags, new.scope, new.memory_type);
END;

CREATE TRIGGER memories_fts_delete AFTER DELETE ON memories
BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, title, content, tags, scope, memory_type)
    VALUES ('delete', old.id, old.title, old.content, old.tags, old.scope, old.memory_type);
END;

CREATE TRIGGER memories_fts_update AFTER UPDATE ON memories
BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, title, content, tags, scope, memory_type)
    VALUES ('delete', old.id, old.title, old.content, old.tags, old.scope, old.memory_type);
    INSERT INTO memories_fts(rowid, title, content, tags, scope, memory_type)
    VALUES (new.id, new.title, new.content, new.tags, new.scope, new.memory_type);
END;
```

### Indexes

```sql
CREATE INDEX idx_memories_type ON memories(memory_type);
CREATE INDEX idx_memories_scope ON memories(scope);
CREATE INDEX idx_memories_status ON memories(status);
CREATE INDEX idx_memories_level ON memories(level);
CREATE INDEX idx_memories_created ON memories(created_at);
CREATE INDEX idx_memories_candidate ON memories(candidate_id);
CREATE INDEX idx_memories_superseded ON memories(superseded_by);
CREATE INDEX idx_events_memory ON memory_events(memory_id);
CREATE INDEX idx_events_type ON memory_events(event_type);
```

### Table: `candidates_processed`

```sql
CREATE TABLE candidates_processed (
    candidate_id TEXT PRIMARY KEY,
    processed_at TEXT NOT NULL,
    action TEXT NOT NULL,             -- promoted, skipped, merged, rejected
    target_memory_id TEXT,            -- if promoted, which memory
    notes TEXT                        -- why this action was taken
);
```

### FTS Index

```sql
CREATE VIRTUAL TABLE memories_fts USING fts5(
    title, content, tags,
    content=memories,
    content_rowid=id
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER memories_fts_insert AFTER INSERT ON memories
BEGIN
    INSERT INTO memories_fts(rowid, title, content, tags)
    VALUES (new.id, new.title, new.content, new.tags);
END;

CREATE TRIGGER memories_fts_delete AFTER DELETE ON memories
BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, title, content, tags)
    VALUES ('delete', old.id, old.title, old.content, old.tags);
END;

CREATE TRIGGER memories_fts_update AFTER UPDATE ON memories
BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, title, content, tags)
    VALUES ('delete', old.id, old.title, old.content, old.tags);
    INSERT INTO memories_fts(rowid, title, content, tags)
    VALUES (new.id, new.title, new.content, new.tags);
END;
```

### Indexes

```sql
CREATE INDEX idx_memories_type ON memories(memory_type);
CREATE INDEX idx_memories_scope ON memories(scope);
CREATE INDEX idx_memories_status ON memories(status);
CREATE INDEX idx_memories_created ON memories(created_at);
CREATE INDEX idx_memories_candidate ON memories(candidate_id);
CREATE INDEX idx_memories_superseded ON memories(superseded_by);
```

---

## Consolidator API

### Core Functions

```python
class Consolidator:
    """Generation 1 consolidator: candidates → SQLite → retrieval"""
    
    def __init__(self, db_path: str, candidates_dir: str):
        """Initialize with database path and candidates directory"""
        
    def promote(self, candidate_id: str) -> str:
        """
        Promote a candidate to stored memory.
        Returns: memory id
        """
        
    def reject(self, candidate_id: str, reason: str):
        """
        Reject a candidate (do not promote).
        Records rejection in candidates_processed.
        """
        
    def merge(self, candidate_ids: list[str], target_memory_id: str):
        """
        Merge multiple candidates into one existing memory.
        Updates target memory content, records merge action.
        """
        
    def search(self, query: str, limit: int = 10) -> list[Memory]:
        """
        Search memories using FTS5.
        Returns: list of Memory objects with scores
        """
        
    def get(self, memory_id: str) -> Memory:
        """
        Retrieve a specific memory by id.
        """
        
    def list(self, 
             memory_type: str = None,
             scope: str = None,
             status: str = 'active',
             limit: int = 100) -> list[Memory]:
        """
        List memories with optional filters.
        """
        
    def update(self, memory_id: str, **changes) -> Memory:
        """
        Update a memory's content or metadata.
        Preserves provenance.
        """
        
    def archive(self, memory_id: str) -> Memory:
        """
        Archive a memory (status → archived).
        Non-destructive.
        """
        
    def supersede(self, old_id: str, new_id: str) -> Memory:
        """
        Mark old memory as superseded by new memory.
        Sets superseded_by on old, derived_from on new.
        """
        
    def rebuild(self, candidates_dir: str) -> int:
        """
        Rebuild entire database from candidates.
        Returns: number of memories created.
        """
        
    def health_check(self) -> dict:
        """
        Run integrity checks:
        - orphaned memories (no candidate source)
        - duplicate content
        - broken supersession links
        - stale candidates
        Returns: dict of issues found
        """
```

### Memory Object

```python
@dataclass
class Memory:
    id: str
    candidate_id: str
    title: str
    content: str
    memory_type: str
    scope: str
    status: str
    created_at: str
    promoted_at: str
    source: str
    source_agent: str | None
    sensitivity: str
    retention: str
    tags: list[str]
    metadata: dict
    superseded_by: str | None
    derived_from: list[str]
    derived_via: str | None
    confidence: float
```

---

## Promoter (Simple Version)

For Gen1, promotion is simple:

```python
class SimplePromoter:
    """
    Simple promotion logic:
    - Read candidate
    - Extract metadata from frontmatter
    - Create memory record
    - Record promotion action
    """
    
    def promote_candidate(self, candidate_path: str) -> Memory:
        # Read candidate markdown
        # Parse frontmatter metadata
        # Generate memory id
        # Insert into database
        # Record in candidates_processed
        # Return Memory object
        pass
```

**Deferred for future generations:**
- LLM-based content extraction
- Smart merging of similar candidates
- Confidence scoring
- Content quality evaluation
- Contradiction detection

---

## Retrieval API

### Basic Search (Gen1)

```python
def search(self, query: str, limit: int = 10) -> list[Memory]:
    """
    FTS5 keyword search.
    Returns memories ranked by relevance score.
    """
    results = self.db.execute(
        """
        SELECT memories.*, memories_fts.rank
        FROM memories
        JOIN memories_fts ON memories.id = memories_fts.rowid
        WHERE memories_fts MATCH ?
        AND memories.status = 'active'
        ORDER BY memories_fts.rank
        LIMIT ?
        """,
        (query, limit)
    )
    return [Memory.from_row(row) for row in results]
```

### Deferred Retrieval Features

- Semantic vector search
- Hybrid BM25 + vector ranking
- RRF fusion
- Graph-based retrieval
- Personalized PageRank
- Temporal boosting
- Confidence-weighted ranking
- Explainable ranking with score breakdown

---

## File Structure

```
memory/memory-consolidator/
├── README.md              # This plan + usage docs
├── PLAN-GEN1.md           # This file
├── src/
│   ├── __init__.py
│   ├── consolidator.py    # Main Consolidator class
│   ├── promoter.py        # SimplePromoter class
│   ├── schema.py          # Memory dataclass
│   ├── database.py        # SQLite setup, migrations
│   └── cli.py             # Command-line interface
├── tests/
│   ├── test_consolidator.py
│   ├── test_promoter.py
│   ├── test_retrieval.py
│   └── fixtures/          # Test candidates
└── migrations/            # Schema evolution
    └── 001_initial.sql
```

---

## CLI Interface

```bash
# Promote all unprocessed candidates
memory-consolidator promote --dir memory/candidates/

# Promote specific candidate
memory-consolidator promote --candidate 20260502-212618-...

# Search memories
memory-consolidator search "context window probe"

# List memories
memory-consolidator list --type fact --scope project:memory-system

# Get specific memory
memory-consolidator get <memory_id>

# Archive memory
memory-consolidator archive <memory_id>

# Rebuild from candidates
memory-consolidator rebuild --dir memory/candidates/

# Health check
memory-consolidator health

# Pi extension tool
memory_consolidator_search "query"
memory_consolidator_list --type fact
```

---

## Pi Extension Integration

### Tools to Register

```typescript
// .pi/extensions/memory-consolidator/index.ts

// Search memories
tool: memory_consolidator_search(query: string)

// List memories with filters
tool: memory_consolidator_list(type?: string, scope?: string)

// Get specific memory
tool: memory_consolidator_get(id: string)

// Promote candidate
tool: memory_consolidator_promote(candidate_id: string)

// Hook: after candidate capture, optionally auto-promote
hook: candidate_captured
```

---

## Success Criteria for Gen1

### Must Have
- [ ] Read candidates from `memory/candidates/`
- [ ] Store candidates as memories in SQLite
- [ ] FTS5 keyword search works
- [ ] Provenance preserved (candidate_id, source, timestamps)
- [ ] Basic lifecycle (create, read, update, archive)
- [ ] Rebuild from candidates works
- [ ] Health check detects basic issues
- [ ] Pi extension tools registered
- [ ] Tests pass

### Nice to Have
- [ ] Simple merge of similar candidates
- [ ] Confidence scoring (manual)
- [ ] Tag-based filtering
- [ ] Supersession support
- [ ] CLI interface

### Future Generations
- [ ] LLM-based extraction/enrichment
- [ ] Semantic vector search
- [ ] Hybrid BM25 + vector ranking
- [ ] Contradiction detection
- [ ] Ontology folding
- [ ] Graph-based retrieval
- [ ] Multi-backend fan-out
- [ ] Hierarchical memory layers
- [ ] Background consolidation jobs
- [ ] Golden query evaluation
- [ ] Activation decay
- [ ] Memory quality scoring

---

## Migration Path to Future Generations

### Gen2: Semantic Search
- Add ONNX embeddings (local, hardware-accelerated)
- Add vector index to SQLite or separate store
- Hybrid BM25 + vector ranking
- Confidence scoring based on retrieval quality
- Golden query evaluation framework

### Gen3: Memory Lifecycle
- Contradiction detection (semantic similarity + temporal analysis)
- Supersession management (temporal belief tracking)
- Activation decay (access frequency → relevance)
- Background consolidation jobs (incremental processing)
- Memory quality scoring (freshness, confidence, usage)

### Gen4: Knowledge Graph
- Entity extraction (people, projects, tools, concepts)
- Relationship modeling (associations, dependencies, hierarchies)
- Graph-based retrieval (PageRank, path analysis)
- Ontology schema (typed concepts, relationships)
- Contradiction resolution (graph-based conflict detection)

### Gen5: Hierarchical Memory
- Memory levels (raw → operational → abstract)
- Level-based retrieval (scoped by abstraction level)
- Cross-level promotion (bottom-up abstraction)
- Context limits per level (different scope/depth)
- Driver constraint enforcement (level N only controls level N-1)

### Gen6: Multi-Backend Fan-Out
- Backend adapter interface
- Fan-out candidates to multiple backends
- Compare retrieval quality across backends
- Backend-specific optimization
- Migration between backends

### Gen7: Ontology Folding
- Automatic concept merging
- Contradiction resolution with provenance
- Belief tracking over time
- Identity coherence maintenance
- Ontology evolution tracking

---

## Implementation Order

1. **Database schema + setup** (~1 day)
2. **Memory dataclass + schema parsing** (~0.5 day)
3. **SimplePromoter** (~0.5 day)
4. **Consolidator core (promote, reject, merge)** (~1 day)
5. **FTS5 search** (~0.5 day)
6. **List, get, update, archive** (~0.5 day)
7. **Rebuild + health check** (~0.5 day)
8. **CLI interface** (~0.5 day)
9. **Pi extension tools** (~0.5 day)
10. **Tests** (~1 day)

**Total estimated: ~6-7 days**

---

## Risks & Mitigations

### Risk: SQLite FTS5 not good enough for semantic search
**Mitigation:** SQLite FTS5 is sufficient for Gen1. Vector search can be added in Gen2 without breaking schema.

### Risk: Candidate format changes break promoter
**Mitigation:** Candidate format is stable (contract). Schema migration path documented.

### Risk: Database becomes single point of truth
**Mitigation:** Database is rebuildable from candidates. Rebuild function implemented.

### Risk: Future ontology needs different schema
**Mitigation:** SQLite schema is extensible. Metadata column allows arbitrary fields. Migration path documented.

---

## Notes

- This is Generation 1: simple, working, extensible
- Not implementing HECM or hierarchical memory yet
- Focus on: candidates → storage → retrieval
- Future iterations will add complexity incrementally
- All deferred features are documented for future reference
