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

## Notes

Triage 2026-11-24, merged from TASK-673 (circuitry): `chitty show CIRCUIT-106` printed 18,415 bytes, mostly `## Notes` and `## History`, which capped tool output truncates in the middle. Ideas: `--brief`, `--no-history`, `--latest-notes N`, or leave History out unless `--full` is passed.

## History

- 2026-11-13T19:52:04Z zesty-umber-puffin → backlog
- 2026-11-24T22:40:09Z zesty-coral-newt: changed notes
