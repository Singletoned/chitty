---
title: Add chitty fix, and run it before every autocommit
status: todo
labels:
  - cli
  - check
created: 2026-10-25
---

## Description

chitty check stays read-only and reports problems. A new chitty fix runs the same checks, fixes what it can, reports what it fixed, and exits non-zero for any problem it cannot fix. When autocommit is on, fix runs on the written files before the commit.

## Acceptance Criteria

- [ ] chitty check never writes files
- [ ] chitty fix fixes what it can and reports each fix
- [ ] chitty fix exits non-zero when problems it cannot fix remain
- [ ] With autocommit on, fix runs on the touched files before committing, and a remaining problem stops the commit
- [ ] PLAN.md, README and the agent guide describe fix
