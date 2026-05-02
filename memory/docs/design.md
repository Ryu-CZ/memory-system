# Memory Architecture Design

## Principles

- Markdown is the canonical source of truth for durable memory.
- Caches, indexes, embeddings, and database files are rebuildable from Markdown.
- Memory should be scoped, useful, and forgettable.
- Retention and review should be explicit enough to prevent stale or unwanted memories from lingering by accident.
- Generated artifacts should support workflows, not replace reviewable source notes.

## Boundaries

- Keep sandbox work in this repository under `memory/`.
- Do not write to the user's general vault or any external memory store from this project setup.
- Do not promote secrets, real credentials, tokens, or sensitive personal data into active durable memory from `memory-inbox`.
- For early YOLO capture-first inbox tests, synthetic secret-like fixtures are allowed when they are explicitly part of the test.
- Treat this workspace as an implementation sandbox, not a production memory vault.

## Data Flow

```text
capture/input -> memory-inbox -> candidate Markdown -> memory-consolidator -> active/reviewed Markdown + rebuilt indexes
```

1. Capture/input arrives as raw or semi-structured memory candidates.
2. `memory-inbox` writes candidate Markdown records first, then records scope, sensitivity, and metadata for later review.
3. `memory-consolidator` reviews candidates against existing canonical Markdown.
4. Approved information becomes active or reviewed Markdown.
5. Derived indexes and caches are rebuilt from the reviewed Markdown corpus.

## Generated Artifacts

Indexes, SQLite databases, embeddings, logs, and similar generated files are derived and disposable unless explicitly documented otherwise. They should be excluded from canonical source review and rebuilt from Markdown whenever needed.
