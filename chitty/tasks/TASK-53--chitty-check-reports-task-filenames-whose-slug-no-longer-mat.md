---
title: chitty check reports task filenames whose slug no longer matches the title
status: todo
created: 2026-10-28
---

## Description

TASK-41 made `chitty fix` rename files whose slug is stale, but `chitty check` exits 0 for them. On 2026-10-28, `check` passed while `fix` then renamed TASK-4, TASK-5, TASK-6 and TASK-40. Every repair `fix` makes should be reportable by `check`, so that a stale filename shows up without anything being written.

## Acceptance Criteria

- [ ] `chitty check` reports each task whose filename slug differs from the slug of its title, naming the expected filename, and exits non-zero
- [ ] `chitty fix` still repairs it, and `check` passes afterwards
- [ ] A regression test fails before the fix and passes after

## History

- 2026-10-28 → todo
