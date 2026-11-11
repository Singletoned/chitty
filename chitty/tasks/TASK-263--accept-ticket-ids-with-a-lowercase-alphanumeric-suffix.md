---
title: Accept ticket IDs with a lowercase alphanumeric suffix
status: cold-read
parent: TASK-262
created: 2026-11-11
---

## Description

- `src/chitty/ids.py` accepts `PREFIX-N` only (`TaskId.number` is an `int`). Also accept a suffix of lowercase letters and digits with at least one letter, for example `BACKLOG-k3f9x2ab`. Input is case-insensitive and stored lowercase.
- It works everywhere an ID does: filenames, `depends_on`, `parent`, `chitty show` and `chitty edit`.
- Sorting: numeric IDs sort as today; alphanumeric ones after them, by suffix. `BACKLOG-48213907` stays numeric.
- Nothing generates these IDs yet; tests write the files directly.

## Acceptance Criteria

- [ ] A ticket file `chitty/backlog/BACKLOG-k3f9x2ab--x.md` written by a test can be shown with `chitty show BACKLOG-K3F9X2AB`, edited, and named in another ticket's `depends_on`. It fails today.
- [ ] `chitty list` shows `BACKLOG-12` before `BACKLOG-k3f9x2ab`, and `chitty check` reports no problem for that file.

## History

- 2026-11-11T11:35:12Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:47Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:39:53Z vivid-yellowhammer backlog → cold-read
