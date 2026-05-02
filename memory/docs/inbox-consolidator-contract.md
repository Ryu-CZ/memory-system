# Inbox to Consolidator Contract

This document defines the initial documentation-only handoff contract between `memory-inbox` and `memory-consolidator`. The exact schema can be formalized later once implementation details are chosen.

## Handoff Directory

Candidate records are written to:

```text
memory/candidates/
```

`memory-inbox` may create candidate files there. It must not promote, merge, deduplicate against the canonical corpus, archive, index, or embed them. Those actions belong to `memory-consolidator` or later memory services.

## Record Format

Candidate records are Markdown files. Each file should contain enough conceptual metadata for a consolidator to review, group, promote, archive, redact, or reject the candidate later.

The inbox is capture-first. Sensitivity fields and triage flags are descriptive metadata, not automatic blockers in the MVP.

## Required Conceptual Metadata

```yaml
id: cand_YYYYMMDD_HHMMSS_hash
status: candidate | needs_review
created_at: YYYY-MM-DDTHH:mm:ssZ
source: user_explicit | observed | imported | inferred | agent_summary | subagent_summary | tool_output
source_agent: main-agent | subagent:<name> | user | extension:<name>
memory_type: project_context | procedure | decision | episode | source | preference | governance
scope: project:<path-or-slug> | global | session:<id> | task:<id>
sensitivity: ordinary | personal | sensitive | secret-prohibited
retention: indefinite | review_by | expire_by | session_only
triage_flags: [] # e.g. yolo_capture_first, dm_private, hidden_lore, secret_like_literal, requires_human_review
```

The body should include:

```markdown
# Short human-readable title

## Proposed Memory

The candidate memory stated narrowly.

## Evidence

Why this candidate exists and where it came from.

## Expected Future Use

What future task this could improve.
```

## Responsibilities

### `memory-inbox`

- Creates candidate Markdown records permissively.
- Performs initial validation of required conceptual metadata.
- Classifies scope, sensitivity, source, retention, and triage flags for later review.
- Hands candidate files to `memory-consolidator` without making durable promotion decisions.
- **Never** promotes candidates into active durable memory.
- **Never** writes indexes, embeddings, or database files.

### `memory-consolidator`

- Consumes candidate Markdown records from `memory/candidates/`.
- Promotes, merges, archives, or rejects candidates according to policy.
- Stores promoted memories in a durable backend (SQLite for Gen1).
- Supports retrieval over accumulated memories.
- Rebuilds storage from candidates if needed.
- Ensures generated artifacts are rebuildable from candidates.

## Notes

- `secret-prohibited` is a promotion/consolidation warning label. It does not block candidate capture in YOLO capture-first mode.
- `needs_review` indicates a candidate that was captured but should receive extra attention before consolidation.
- `session_only` retention indicates content should not be promoted to durable memory by default.
- Future stricter modes may add extra rejection metadata, but they are not part of the MVP capture-first path.
- Future implementations may encode this metadata as YAML frontmatter, sidecar files, or another documented Markdown-compatible convention.
