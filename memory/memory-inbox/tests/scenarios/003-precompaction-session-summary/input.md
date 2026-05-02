# Scenario 003: Pre-Compaction Session Summary

## Invocation

Tool/command path: `memory-inbox precompact`

## Input Text

Before context compression, the main agent summarizes the session:

> In this session we decided to build memory-inbox as a Pi extension product surface backed by a deterministic CLI/library core. The extension is the always-available Pi integration; the CLI/library owns validation and repeatable tests. memory-inbox only writes memory candidates and must not promote durable memory. The first repeatable scenarios are explicit sandbox permission, secret-like capture-first, and pre-compaction episode capture.

## Caller Metadata

```yaml
source: agent_summary
source_agent: main-agent
memory_type: episode
scope: project:/home/trval/projects/chats/pi_sandbox/memory
sensitivity: ordinary
retention: review_by
triage_flags:
  - pre_compaction_capture
```

## Expected Product Behavior

Create one candidate Markdown record of type `episode`. It should preserve the product decision and test scenario list as a candidate for later consolidation. It should not update active memory or indexes.
