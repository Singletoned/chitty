---
title: Match TASK-291 to the planned `taidy security --json` shape
status: backlog
created: 2026-11-22
---

## Description

Taidy planned the command as TASK-15 (parent TASK-14) in the taidy repository. `taidy security --json PATH` will print an object `{"findings": [...], "errors": [...]}`, not a bare list. Each finding has `tool`, `rule`, `file`, `line` (integer or null) and `message`. Each error (a file a scanner could not scan) has `tool`, `file` and `message`. It exits 0 when the scanners ran and 1 when a scanner is missing or fails. The first version runs bandit only; pip-audit, npm audit and trivy follow as TASK-16, TASK-17 and TASK-18. `taidy docker` currently drops `--json` (taidy TASK-19), so run taidy directly until that lands.

## Notes

Suggestion origin: taidy

Merged into TASK-291 as a note; archived.

## History

- 2026-11-22T13:16:26Z friendly-jade-stoat → backlog
- 2026-11-22T13:16:27Z friendly-jade-stoat: changed notes
- 2026-11-22T13:18:52Z friendly-jade-stoat: changed notes
- 2026-11-22T13:18:54Z friendly-jade-stoat backlog → archived
