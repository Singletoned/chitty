---
title: Read tickets with any prefix from every directory under `chitty/`
status: todo
parent: TASK-262
created: 2026-11-11
---

## Description

- Today Chitty finds tickets only in configured contexts. Also read every other directory directly under `chitty/`, and its `archive/`, so existing `HUMAN-` and `BACKLOG-` tickets keep working once contexts are removed (TASK-267).
- Lookup is by full ID, not by prefix, in any directory under `chitty/`; one directory may hold several prefixes, and a configured prefix may sit in an unconfigured directory. That changes `context_of`, `find` and `_dependency_is_done` in `src/chitty/store.py`. A ticket's context name is its directory name.
- Reading only: `chitty show`, `chitty list`, `chitty check`, and `depends_on` in `check` and in `chitty next`. `chitty next` and `chitty run` select only tickets in configured contexts; the others count only as dependencies.
- Writes (`edit`, `archive`) on those tickets fail with a plain Chitty error, not a `KeyError`, until TASK-280.
- `chitty check` without `-c` covers every directory under `chitty/` (`check_` in `src/chitty/cli.py` and the context filter at the end of `check()` in `src/chitty/check.py`) and treats those files as it treats a configured context. `-c` still takes configured names only. The same ID in two directories is a `check` error naming both paths.
- Historical discovery from other branches covers those directories: relax the prefix filters in `_tasks_in_location` and `scan` in `src/chitty/store.py`.

## Acceptance Criteria

- [ ] A test writes `chitty/other/OTHER-1--x.md` and `chitty/other/archive/OTHER-2--y.md`, with no `other` context in `chitty.toml`. `chitty show OTHER-1` and `chitty show OTHER-2` work, and `chitty list` includes `OTHER-1`. It fails today.
- [ ] A `todo` ticket with `depends_on: [OTHER-1]` passes `chitty check`, and while `OTHER-1` is unfinished `chitty next` neither fails with a dependency error nor selects either ticket.
- [ ] `OTHER-1` in both `chitty/other/` and `chitty/more/` makes `chitty check` fail, naming both paths.
- [ ] `chitty edit OTHER-1 -s doing` fails with a Chitty error naming the directory, not a traceback.

## Notes

Possible starting point for tests: `git show refs/cold-read/TASK-266/2:tests/test_unconfigured_directories.py`. Check it against the current criteria; do not trust it.

## History

- 2026-11-11T11:35:15Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:48Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T13:39:54Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T13:42:22Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:42:29Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T13:42:29Z vivid-yellowhammer cold-read → planning
- 2026-11-11T13:44:11Z vivid-yellowhammer planning → cold-read
- 2026-11-11T13:46:10Z vivid-yellowhammer: changed description, acceptance criteria, notes
- 2026-11-11T13:46:10Z vivid-yellowhammer cold-read → todo
