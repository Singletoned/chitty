---
title: Read tickets with any prefix from every directory under `chitty/`
status: doing
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
- [x] A `todo` ticket with `depends_on: [OTHER-1]` passes `chitty check`, and while `OTHER-1` is unfinished `chitty next` neither fails with a dependency error nor selects either ticket.
- [x] `OTHER-1` in both `chitty/other/` and `chitty/more/` makes `chitty check` fail, naming both paths.
- [x] `chitty edit OTHER-1 -s doing` fails with a Chitty error naming the directory, not a traceback.

## Plan

Add repository-wide discovery for ticket directories while keeping selection and write targets restricted to configured contexts. Resolve IDs by scanning full IDs across configured and extra directories; use discovered context metadata for show/list/dependencies and reject writes to unconfigured contexts with ChittyError. Expand check defaults and duplicate detection, while preserving -c configured-only semantics. Relax historical prefix filtering. Add focused unittest coverage for active/archive reads, dependency and next behavior, duplicate IDs, and write errors; first run regression tests unfixed, then make the implementation, run format/check, inspect status, commit code, and update verified criteria.

## Notes

Possible starting point for tests: `git show refs/cold-read/TASK-266/2:tests/test_unconfigured_directories.py`. Check it against the current criteria; do not trust it.

Verified: regression tests fail before the implementation and pass afterward. `chitty next` reports its normal no-ticket exit when the only eligible ticket is blocked; the test verifies it does not report a dependency error or select either ticket.

Review failed (tests): Add regression coverage and support for mixed prefixes in configured directories, as the description requires full-ID lookup in any directory. A throwaway CliRunner test placed OTHER-1 in chitty/tasks; both show OTHER-1 and check exited 1 with "prefix OTHER does not belong in context tasks (prefix TASK)". make format and make check passed.

1: fail - The specified example passes, but full-ID discovery still rejects other prefixes in configured directories.
2: pass - Dependency check and next exercised.
3: pass - Duplicate paths reported.
4: pass - Edit reports a plain error.

## Summary

Implemented full-ID discovery and reading from unconfigured ticket directories, including archives; preserved configured-context selection and write restrictions. Verified all four acceptance criteria with tests/test_unconfigured_directories.py. Verification: focused tests, make format, and make check pass. Follow-up: TASK-280 owns writing tickets in unconfigured contexts.

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
- 2026-11-11T13:59:25Z friendly-eel todo → doing
- 2026-11-11T13:59:53Z friendly-eel: wrote the plan
- 2026-11-11T14:06:49Z friendly-eel: changed notes, summary; ticked acceptance criteria
- 2026-11-11T14:06:49Z friendly-eel doing → review
- 2026-11-11T14:10:40Z brisk-jay: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-11T14:10:40Z brisk-jay review → doing
