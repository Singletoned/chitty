---
title: Add trivy to the audit
status: backlog
depends_on:
  - TASK-291
parent: TASK-290
created: 2026-11-11
---

## Description

- Add a `trivy fs --scanners vuln,secret,misconfig --format json .` adapter to `scripts/audit.py`, one suggestion per (finding ID, file), titled `Audit: trivy <ID> in <file>`. trivy is a system install (`brew install trivy`); a missing trivy fails the audit with that instruction. Document it in `README.md`.

## Acceptance Criteria

- [ ] A test with a committed fake secret in a temporary repository gets one trivy suggestion naming the file. It fails today.

## Notes

Moved to taidy, 2026-11-11: the scanners belong in `taidy security`.

## History

- 2026-11-11T16:18:26Z vivid-yellowhammer → backlog
- 2026-11-11T18:59:37Z vivid-yellowhammer: changed notes
