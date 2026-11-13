---
title: Re-cold-read dependent tickets when contracts complete
status: backlog
labels:
  - workflow
  - planning
priority: medium
created: 2026-11-13
---

## Description

A ticket cold-read before an architecture or specification dependency completes may rely on a contract that later changes.

## Acceptance Criteria

- [ ] A dependency completion can mark eligible dependent tickets as requiring a fresh cold read.
- [ ] A dependent ticket requiring a fresh cold read is excluded from todo and doing selection until the cold read is complete.
- [ ] The fresh cold read receives the completed dependency output and records its result in ticket history.
- [ ] Tickets without the relevant dependency relationship keep their existing workflow.

## History

- 2026-11-13T19:51:57Z zesty-umber-puffin → backlog
