---
title: Add `chitty renumber` to repair tickets sharing an ID
status: backlog
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

- [ ] A test with two files sharing `TASK-24` shows `chitty renumber <path>` moving only that file to the next number, recording `moved_from`, `chitty check` then passing, and tickets naming `TASK-24` listed and unchanged

## History

- 2026-11-05T14:43:40Z mellow-newt → backlog
- 2026-11-05T14:46:38Z mellow-newt: changed dependencies, description, acceptance criteria
- 2026-11-05T14:46:39Z mellow-newt: changed acceptance criteria
