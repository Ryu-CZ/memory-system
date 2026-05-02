# Memory Consolidator

`memory-consolidator` is the downstream consolidation layer for the memory workspace. It is deferred while `memory-inbox` is the active MVP focus.

## Purpose

Review candidate Markdown and existing canonical Markdown to deduplicate, summarize, detect stale notes, check retention, and rebuild generated indexes.

## Inputs

- Candidate Markdown records from `memory-inbox`.
- Existing canonical Markdown memory.
- Future review policy or retention metadata.

## Outputs

- Reviewed Markdown updates.
- Promoted, merged, archived, or rejected candidate records.
- Derived indexes and caches rebuilt from canonical Markdown.

## Non-goals

- No raw capture user experience.
- No promotion of real secrets, credentials, or tokens into active durable memory; consolidator may inspect, redact, archive, or reject inbox candidates that contain secret-like evidence.
- No treatment of SQLite databases, vector stores, embeddings, logs, or other generated artifacts as canonical memory.
- No permanent reliance on caches that cannot be rebuilt from Markdown.

## Future Implementation Areas

Future source, tests, and examples may cover:

- Candidate grouping and deduplication.
- Summarization workflows.
- Retention and expiry review.
- Stale note detection.
- Promotion/rejection/archive decisions.
- Rebuilding indexes from Markdown after deleting generated caches.
- Synthetic duplicate candidates, stale metadata, and simple Markdown corpora.

No programming language or runtime has been selected yet.
