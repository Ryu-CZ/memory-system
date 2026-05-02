---
id: cand_20260427_135147_337f607ffa
status: candidate
created_at: 2026-04-27T13:51:47Z
source: agent_summary
source_agent: extension:memory-inbox
memory_type: episode
scope: project:/home/trval/projects/chats/pi_sandbox
sensitivity: ordinary
retention: review_by
triage_flags:
  - pre_compaction_capture
---

# Pre-Compaction Memory Inbox Episode

## Proposed Memory

- memory-inbox is a Pi extension product surface
- deterministic CLI/library core
- candidate-only boundary
- explicit sandbox permission scenario
- secret-like capture-first scenario
- pre-compaction episode capture scenario

## Evidence

Captured by `precompact` from `agent_summary` via `extension:memory-inbox`.

Original input:

> Pi session_before_compact hook fired. tokensBefore=211830. firstKeptEntryId=a7bfdb04.

## Expected Future Use

A future memory-consolidator can review this candidate, decide whether it becomes canon, and preserve or transform it according to its own downstream policy. Scope: `project:/home/trval/projects/chats/pi_sandbox`. Retention hint: `review_by`.
