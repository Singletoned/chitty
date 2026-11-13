---
title: Add compact output for inspection commands
status: backlog
labels:
  - cli
  - workflow
priority: medium
created: 2026-11-13
---

## Description

Coding agents need concise deterministic text for read-only inspection without changing the human-facing default output or replacing the JSON contract.

## Acceptance Criteria

- [ ] chitty list, chitty show, and chitty inbox accept --llm-friendly.
- [ ] Compact output preserves the normal records, ordering, statuses, priorities, labels, and suggestion content without decorative headings.
- [ ] The format has documented truncation and field-selection rules and remains human-readable text.
- [ ] JSON output remains the machine-readable contract and is unchanged.
- [ ] Tests lock down stable output and option behavior for each supported command.

## History

- 2026-11-13T19:52:04Z zesty-umber-puffin → backlog
