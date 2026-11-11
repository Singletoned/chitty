---
title: Add `npm audit` to the audit
status: backlog
depends_on:
  - TASK-291
parent: TASK-290
created: 2026-11-11
---

## Description

- Add an `npm audit --json` adapter to `scripts/audit.py`, one suggestion per vulnerable package, titled `Audit: npm <package> <advisory ID>`. The Node dependencies are only the pinned prettier used by tests.

## Acceptance Criteria

- [ ] A test feeding the adapter recorded `npm audit --json` output with one advisory gets one suggestion naming the package and advisory. It fails today.

## History

- 2026-11-11T16:18:25Z vivid-yellowhammer → backlog
