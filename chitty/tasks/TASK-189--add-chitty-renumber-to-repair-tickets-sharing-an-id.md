---
title: Add `chitty renumber` to repair tickets sharing an ID
status: backlog
priority: high
parent: TASK-106
created: 2026-11-05
---

## Description

When two tickets share an ID after a merge, the repair today is hand-editing task files and every reference, and `chitty fix` cannot do it. `Repo.find` raises `is used by more than one file`, so the command cannot take an ID.

Add `chitty renumber <PATH>`, taking the path of the one file to change. It gives that file the next number in its context, using `next_number`, keeps its slug, and records `moved_from` as `Repo.move` does. It refuses a path that is not a task file in a context, or whose ID no other file uses, because `chitty move` covers ordinary moves and renumbering a unique ID only breaks references.

It must not rewrite references in other tickets, because a `depends_on` or `parent` naming a shared ID cannot say which file it meant. Instead it prints each ticket that names the old ID, in those fields, for a person to check. Follow `move` for committing. `cli.py` and `mcp.py` stay thin and offer the same command, as `PLAN.md` asks of commands.

`echonomicon` needs this for its existing duplicates, though running it there is for that repository's own session.

## Acceptance Criteria

- [ ] A test with two files sharing `TASK-24` shows `chitty renumber <path>` moving only that file to the next number, recording `moved_from`, `chitty check` then passing, and tickets naming `TASK-24` listed and unchanged
- [ ] Tests show it refusing a path outside a context and a ticket whose ID is unique, with no file changed
- [ ] `README.md` and `PLAN.md` describe it, and `chitty renumber --help` works through both the CLI and MCP

## History

- 2026-11-05T14:43:40Z mellow-newt → backlog
