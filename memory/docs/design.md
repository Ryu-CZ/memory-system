# Memory Architecture Design

## Principles

- **Candidate extraction is the stable boundary**. Capture durable candidate records first; backends are swappable.
- **Markdown is the canonical format for candidates**. Candidate records are human-readable, git-friendly, and rebuildable.
- **Backends are intentionally swappable**. Storage, indexing, retrieval, and graphing can vary. Backends do not need to be Markdown-native.
- **Local does not mean simple**. Local means owned, durable, private, and permanent. Complexity is justified for serious personal memory.
- **Generated artifacts are rebuildable**. Caches, indexes, embeddings, and database files must be regenerable from candidates.
- **Memory should be scoped, useful, and forgettable**. Retention and review should be explicit.
- **Provenance is first-class**. Every memory traces back to its source candidate.

## Boundaries

- Keep project work in this repository under `memory/`.
- Do not write to the user's general vault or any external memory store from this project setup.
- Do not promote secrets, real credentials, tokens, or sensitive personal data into active durable memory from `memory-inbox`.
- For early YOLO capture-first inbox tests, synthetic secret-like fixtures are allowed when they are explicitly part of the test.
- Treat this workspace as an implementation project, not a production memory vault.

## Data Flow

```text
capture/input -> memory-inbox -> candidate Markdown -> memory-consolidator -> storage backend -> retrieval
```

1. Capture/input arrives as raw or semi-structured memory candidates.
2. `memory-inbox` writes candidate Markdown records first, then records scope, sensitivity, and metadata for later review.
3. `memory-consolidator` consumes candidates and stores them in a durable backend (SQLite for Gen1).
4. Stored memories support keyword retrieval (FTS5 for Gen1).
5. Derived indexes and caches are rebuildable from candidates.

## Generated Artifacts

Indexes, SQLite databases, embeddings, logs, and similar generated files are derived and disposable unless explicitly documented otherwise. They should be excluded from canonical source review and rebuilt from candidates whenever needed.
