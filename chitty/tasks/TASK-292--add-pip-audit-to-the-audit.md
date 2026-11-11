---
title: Add pip-audit to the audit
status: backlog
depends_on:
  - TASK-291
parent: TASK-290
created: 2026-11-11
---

## Description

- Add a pip-audit adapter to `scripts/audit.py`: audit the locked dependencies (`uv export` piped to `pip-audit -r`), one suggestion per vulnerable package, titled `Audit: pip-audit <package> <vulnerability ID>`.

## Acceptance Criteria

- [ ] A test with a requirements file pinning a package with a known vulnerability gets one suggestion naming the package and ID. It fails today.

## History

- 2026-11-11T16:18:24Z vivid-yellowhammer → backlog
