---
id: cand_20260427_120000_fd6c82c8b2
status: candidate
created_at: 2026-04-27T12:00:00Z
source: agent_summary
source_agent: main-agent
memory_type: episode
scope: project:/home/trval/projects/chats/pi_sandbox/memory/memory-inbox
sensitivity: ordinary
retention: review_by
triage_flags:
  - implementation_progress
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

Captured by `capture` from `agent_summary` via `main-agent`.

Original input:

> Implemented memory-inbox deterministic Python CLI/library core and project-local Pi extension adapter. The core supports capture, precompact, validate, eval, and list commands. The project-local extension under .pi/extensions/memory-inbox registers memory_inbox_capture, /memory-inbox, /memory-candidates, and session_before_compact. Validation currently passes 13 unittest tests and all three repeatable scenarios. Next step is live Pi reload/use testing of the extension, then candidate review/list UX improvements.

## Expected Future Use

A future memory-consolidator can review this candidate, decide whether it becomes canon, and preserve or transform it according to its own downstream policy. Scope: `project:/home/trval/projects/chats/pi_sandbox/memory/memory-inbox`. Retention hint: `review_by`.
