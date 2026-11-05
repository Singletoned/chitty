---
title: Add `chitty renumber` to repair tickets sharing an ID
status: done
priority: high
depends_on:
  - TASK-177
parent: TASK-106
created: 2026-11-05
---

## Description

When two tickets share an ID after a merge, the repair today is hand-editing task files and every reference, and `chitty fix` cannot do it. Two files with one ID cannot be addressed by that ID: `_tasks_in_location` in `src/chitty/store.py` keys tickets by `TaskId`, so they collapse into one, and `chitty show`, `edit` and `list` silently use one of them. `chitty check` does report the pair, through `scan`. `find` raises `is used by more than one file` only when one copy is active and the other archived.

Add `chitty renumber <PATH>`, taking the path of the one file to change. A new `Repo.renumber(path)` locates the file by path through `scan`, never through `find` or `all_tasks`, which would hide it. It gives that file the next number in its context, using `next_number`, keeps its slug, and records `moved_from`, sharing a helper with `Repo.move`, which takes an ID and cannot be reused directly. It refuses a path that is not a task file in a context, or whose ID no other file uses, because `chitty move` covers ordinary moves and renumbering a unique ID only breaks references.

It must not rewrite references in other tickets, because a `depends_on` or `parent` naming a shared ID cannot say which file it meant. Instead it prints each ticket that names the old ID, in those fields, for a person to check. `chitty check` cannot catch a wrong one, because the old ID still resolves to the remaining file. Follow `move` for committing. `cli.py` and `mcp.py` stay thin and offer the same command, as `PLAN.md` asks of commands.

`echonomicon` needs this for its existing duplicates, though running it there is for that repository's own session.

## Acceptance Criteria

- [x] A test with two files sharing `TASK-24` shows `chitty renumber <path>` moving only that file to the next number, recording `moved_from`, `chitty check` then passing, and tickets naming `TASK-24` listed and unchanged
- [x] Tests show it refusing a path outside a context and a ticket whose ID is unique, with no file changed, and accepting an archived path and a path relative to the working directory
- [x] `README.md` and `PLAN.md` describe it, `chitty renumber --help` works, and `renumber` is in the MCP tool list with a description, including the parity test in `tests/test_mcp.py` and the list in `PLAN.md`

## Plan

1. Tests first in a new `tests/test_renumber.py`: two files sharing `TASK-24`, renumber one by path, check `moved_from`, the new number, `chitty check` passing and referencing tickets listed and unchanged; refusals (outside a context, unique ID) changing nothing; archived and relative paths; MCP parity.
2. `Repo.renumber(path)` in `store.py`: locate the file through `scan` across contexts, refuse before `_prepare_write` so a refusal changes nothing, take `next_number`, and share a relocation helper with `move` (new path, `moved_from`, unlink). Return the change and the tickets whose `depends_on` or `parent` name the old ID.
3. Thin `chitty renumber PATH` and MCP `renumber` tool; `README.md` and `PLAN.md` (command list and MCP).

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. Serious, fixed: my premise was wrong. It reproduced a merge leaving two files with one ID: they collapse into one ticket in `show`, `edit` and `list`, so the command must find files through `scan`, and `move` cannot be reused directly. Also fixed: depending on `TASK-177`, since a number chosen from this checkout alone could recreate the collision; MCP having no `--help`; and archived and relative paths.

Owner set to human only so chitty run leaves this ticket to this session; cleared when it goes to review.

Found while sharing the helper: `Repo.move` reused the name `task` in its loop over `all_tasks()`, so it returned, and with `autocommit` titled its commit with, the last ticket scanned rather than the moved one. `chitty move HUMAN-1 tasks --json` reported `Zzz other`. Fixed through `_relocate`, with a regression test in `tests/test_renumber.py` seen failing first.

Choices: `renumber` validates before `_prepare_write`, so a refusal changes nothing; the JSON (CLI and MCP alike) is `{task, references: [{id, path}]}`, because the references are the point; `PLAN.md`'s MCP list also gains `next`, which was missing. Checked in a real Git repository with `autocommit`: one commit, recorded as a rename, clean tree.

Reviewed: all acceptance criteria verified independently; targeted tests and make check pass (276 Python tests and Node tests).

## Summary

Added `chitty renumber PATH` and the MCP `renumber` tool over `Repo.renumber` in `store.py`. It locates the file through `scan`, refuses a non-task path or a unique ID, gives it the next number in its context with `moved_from` (archived files stay archived), commits like `move`, and lists tickets whose `depends_on` or `parent` name the old ID without rewriting them. `move` now shares `_relocate`, which fixes it reporting the wrong ticket. Documented in `README.md` and `PLAN.md`.

Verified: `tests/test_renumber.py` (seen failing first) and the MCP parity test; `make check` passes (276 tests plus Node); a manual autocommit run in a scratch repo. Follow-up: running it on `echonomicon`'s duplicates is for that repository's session.

## History

- 2026-11-05T14:43:40Z mellow-newt → backlog
- 2026-11-05T14:46:38Z mellow-newt: changed dependencies, description, acceptance criteria
- 2026-11-05T14:46:39Z mellow-newt: changed acceptance criteria
- 2026-11-05T14:46:40Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T14:46:41Z mellow-newt backlog → todo
- 2026-11-05T21:14:08Z youthful-toad: changed owner, notes
- 2026-11-05T21:20:52Z youthful-toad: wrote the plan
- 2026-11-05T21:20:52Z youthful-toad todo → doing
- 2026-11-05T21:27:20Z youthful-toad: ticked acceptance criteria
- 2026-11-05T21:27:21Z youthful-toad: changed owner, notes, summary
- 2026-11-05T21:27:21Z youthful-toad doing → review
- 2026-11-05T22:20:46Z witty-lapwing: changed notes
- 2026-11-05T22:20:46Z witty-lapwing review → done
