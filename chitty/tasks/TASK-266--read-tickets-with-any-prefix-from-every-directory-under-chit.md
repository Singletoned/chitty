---
title: Read tickets with any prefix from every directory under `chitty/`
status: planning
parent: TASK-262
created: 2026-11-11
---

## Description

- Today Chitty finds tickets only in configured contexts (`Repo.context_of` and `check` in `src/chitty/store.py` and `src/chitty/check.py`; `_tasks_in_location` filters historical files from `src/chitty/git.py`). Also read every other directory directly under `chitty/`, and its `archive/`, so existing `HUMAN-` and `BACKLOG-` tickets keep working once contexts are removed.
- A ticket there is found by its full ID, whatever its prefix; one directory may hold several prefixes. Its context name is the directory name.
- Reading only: `chitty show`, `chitty list`, `chitty check`, and `depends_on` in `check` and in `chitty next`. Writes are `TASK-280`. `-c` with an unconfigured name is out of scope: contexts are going away (TASK-267).
- `chitty check` treats those files as it treats files in a configured context. The same ID in two directories is a `check` error naming both paths.
- Historical discovery from other branches covers those directories too.

## Acceptance Criteria

- [ ] A test writes `chitty/other/OTHER-1--x.md` and `chitty/other/archive/OTHER-2--y.md`, with no `other` context in `chitty.toml`. `chitty show OTHER-1` and `chitty show OTHER-2` work, and `chitty list` includes `OTHER-1`. It fails today.
- [ ] A `todo` ticket with `depends_on: [OTHER-1]` passes `chitty check`, and `chitty next` neither errors nor picks it while `OTHER-1` is unfinished.
- [ ] `OTHER-1` in both `chitty/other/` and `chitty/more/` makes `chitty check` fail, naming both paths.

## History

- 2026-11-11T11:35:15Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:48Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T13:39:54Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:42:22Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:42:29Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T13:42:29Z vivid-yellowhammer cold-read → planning
