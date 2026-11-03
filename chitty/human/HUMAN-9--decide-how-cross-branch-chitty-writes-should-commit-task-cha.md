---
title: Decide how cross-branch Chitty writes should commit task changes
status: done
created: 2026-11-03
---

## Description

TASK-105 requires a durable Git-plumbing design for routing single-ticket writes to another branch, including no-checkout commits, atomic ref updates, error recovery, and multi-path operations such as rename/archive. Decide whether to split the work and approve the intended transactional guarantees.

## Acceptance Criteria

- [x] Choose the required transactional and recovery guarantees for cross-branch writes
- [x] Decide whether TASK-105 should be split into separately reviewable implementation tickets

## Summary

Decided with the human, 2026-11-03: do not route writes to other branches, so no transactional guarantees are needed. Chitty refuses a write when the ticket's latest version is on another branch and names the branch and worktree. `TASK-105` is rewritten as that small ticket, so no split is needed.

## History

- 2026-11-03T09:45:07Z mellow-marten → todo
- 2026-11-03T10:40:59Z lively-panda: changed summary; ticked acceptance criteria
- 2026-11-03T10:40:59Z lively-panda todo → done
