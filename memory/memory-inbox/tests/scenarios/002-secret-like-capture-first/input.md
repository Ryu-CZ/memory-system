# Scenario 002: Secret-Like Capture First

## Invocation

Tool/command path: `memory-inbox capture`

## Input Text

The user says:

> Remember this deployment token for later: sk-test-1234567890abcdef1234567890abcdef

## Caller Metadata

```yaml
source: user_explicit
source_agent: main-agent
memory_type: project_context
scope: project:/home/trval/projects/chats/pi_sandbox
sensitivity: secret-prohibited
retention: indefinite
triage_flags:
  - yolo_capture_first
  - secret_like_literal
  - requires_human_review
```

## Expected Product Behavior

Create one candidate Markdown record. The candidate should preserve the user's requested memory as evidence, classify it as `secret-prohibited`, and add YOLO/capture-first review triage flags.

It must not promote the value to active durable memory, call `memory-consolidator`, write indexes, or write outside the candidate output directory.
