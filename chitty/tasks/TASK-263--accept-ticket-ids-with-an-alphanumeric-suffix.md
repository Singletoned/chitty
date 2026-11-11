---
title: Accept ticket IDs with an alphanumeric suffix
status: done
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

- [x] A ticket file `chitty/backlog/BACKLOG-K3F9X2AB--x.md` with title `x`, written by a test, can be shown with `chitty show backlog-k3f9x2ab`, edited, and named in another ticket's `depends_on`. It fails today.
- [x] `chitty list` shows `BACKLOG-12` before `BACKLOG-K3F9X2AB`, `chitty check` reports no problem, and `chitty add -c backlog` next to them still succeeds.
- [x] `BACKLOG-013` is still rejected as an ID, with an error saying `expected PREFIX-N or PREFIX-SUFFIX`, and `BACKLOG-0A` is accepted.

## Plan

Update TaskId parsing and mixed numeric/alphanumeric ordering, adapt selection ordering and numeric ID allocation scans, then add regression coverage for CLI/file/reference behavior and validation. Review the cold-read diff against current criteria rather than applying it blindly; run focused tests, then format and full checks.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-263/2`, which keeps `TaskId.number` as `int | str`. Check it against the current criteria; do not trust it. It keeps the old error text. Shell completion order (`_complete_task_id` in `cli.py`) is out of scope; it already sorts by string.

Implemented alphanumeric suffix parsing, canonicalization, mixed sorting, and numeric-only allocation scans. Focused 15 tests and full make check passed (483 Python suites plus Node tests); chitty fix completed. Existing chitty fix warnings in unrelated task files remain.

Reviewed: make format && make check passed; also exercised CLI edit and parent in a temporary test.
1: pass - Show, edit and dependency verified.
2: pass - List ordering, check and add verified.
3: pass - Padded numeric rejection and alphanumeric acceptance verified.

## Summary

Implementation committed as a4ace8a (Task: TASK-263). Verified all three acceptance criteria with focused regression tests and full make check. No follow-up required.

## History

- 2026-11-11T11:35:12Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:47Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:39:53Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:43:23Z vivid-yellowhammer: changed title, description, acceptance criteria
- 2026-11-11T13:43:23Z vivid-yellowhammer cold-read → planning
- 2026-11-11T13:44:10Z vivid-yellowhammer planning → cold-read
- 2026-11-11T13:47:07Z vivid-yellowhammer: changed acceptance criteria, notes
- 2026-11-11T13:47:07Z vivid-yellowhammer cold-read → todo
- 2026-11-11T13:55:07Z friendly-adder todo → doing
- 2026-11-11T13:55:26Z friendly-adder: wrote the plan
- 2026-11-11T13:57:27Z friendly-adder: changed notes, summary; ticked acceptance criteria
- 2026-11-11T13:57:27Z friendly-adder doing → review
- 2026-11-11T14:00:10Z rosy-wren: changed notes; ticked acceptance criteria
- 2026-11-11T14:00:10Z rosy-wren review → done
