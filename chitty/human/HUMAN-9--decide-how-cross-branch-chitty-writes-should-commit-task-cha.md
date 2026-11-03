---
title: Decide how cross-branch Chitty writes should commit task changes
status: todo
created: 2026-11-03
---

## Description

TASK-105 requires a durable Git-plumbing design for routing single-ticket writes to another branch, including no-checkout commits, atomic ref updates, error recovery, and multi-path operations such as rename/archive. Decide whether to split the work and approve the intended transactional guarantees.

## Acceptance Criteria

- [ ] Choose the required transactional and recovery guarantees for cross-branch writes
- [ ] Decide whether TASK-105 should be split into separately reviewable implementation tickets

## History

- 2026-11-03T09:45:07Z mellow-marten → todo
