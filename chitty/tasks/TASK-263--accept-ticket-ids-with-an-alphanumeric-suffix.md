---
title: Accept ticket IDs with an alphanumeric suffix
status: cold-read
parent: TASK-262
created: 2026-11-11
---

## Description

- `src/chitty/ids.py` accepts `PREFIX-N` only (`TaskId.number` is an `int`). Also accept a suffix of letters and digits with at least one letter, for example `BACKLOG-K3F9X2AB`; a leading zero is fine there (`BACKLOG-0A`). Like prefixes, suffixes are upper-case in files and case-insensitive on input, so the existing upper-case rules in `check` and `fix` apply unchanged.
- It works everywhere an ID does: filenames, `depends_on`, `parent`, `chitty show` and `chitty edit`.
- Sorting: numeric IDs sort as today; alphanumeric ones after them, by suffix. `BACKLOG-48213907` stays numeric. `TaskId` must stay orderable when both kinds are mixed (`selection.py` `_id_key` too).
- `next_number` and the deleted-number scan in `src/chitty/store.py` ignore alphanumeric IDs, so `chitty add` still works next to one.
- Nothing generates these IDs yet; tests write the files directly.

## Acceptance Criteria

- [ ] A ticket file `chitty/backlog/BACKLOG-K3F9X2AB--x.md` written by a test can be shown with `chitty show backlog-k3f9x2ab`, edited, and named in another ticket's `depends_on`. It fails today.
- [ ] `chitty list` shows `BACKLOG-12` before `BACKLOG-K3F9X2AB`, `chitty check` reports no problem, and `chitty add -c backlog` next to them still succeeds.
- [ ] `BACKLOG-013` is still rejected as an ID, and `BACKLOG-0A` is accepted.

## History

- 2026-11-11T11:35:12Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:47Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:39:53Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:43:23Z vivid-yellowhammer: changed title, description, acceptance criteria
- 2026-11-11T13:43:23Z vivid-yellowhammer cold-read → planning
- 2026-11-11T13:44:10Z vivid-yellowhammer planning → cold-read
