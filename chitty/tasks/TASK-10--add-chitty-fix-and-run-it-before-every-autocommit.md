---
title: Add chitty fix, and run it before every autocommit
status: done
labels:
  - cli
  - check
created: 2026-10-25
---

## Description

chitty check stays read-only and reports problems. A new chitty fix runs the same checks, fixes what it can, reports what it fixed, and exits non-zero for any problem it cannot fix. When autocommit is on, fix runs on the written files before the commit.

## Acceptance Criteria

- [x] chitty check never writes files
- [x] chitty fix fixes what it can and reports each fix
- [x] chitty fix exits non-zero when problems it cannot fix remain
- [x] With autocommit on, fix runs on the touched files before committing, and a remaining problem stops the commit
- [x] PLAN.md, README and the agent guide describe fix

## Plan

Add a shared fix operation that runs checks over the requested scope, reports repairs and unresolved problems, expose it via CLI/MCP, and invoke it on existing touched files before autocommit. The subsequent case-canonicalization task will provide the first remediable check finding.

## Notes

Question: What existing check failures are safe to repair automatically? Answer: none of the current parse, duplicate, dangling, or cycle errors are safe. The first repair is upper-casing stored depends_on IDs from TASK-4; all other problems remain loud failures.

Verified: check remains read-only; fix reports canonical dependency repairs and unresolved errors; autocommit runs fix before Git commit, as covered by an integration test. Documentation and make check pass.
