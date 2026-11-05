---
title: Keep tickets in random-ID contexts in `backlog`
status: backlog
priority: high
depends_on:
  - TASK-190
parent: TASK-106
created: 2026-11-05
---

## Description

Second of three parts, after `TASK-190`. A ticket in a context with `random_ids` waits to be assessed, so it is always `backlog`, and leaves only by being moved. `Repo.add` forces the status to `backlog`, whatever `-s` says, and the check in `src/chitty/cli.py` that a description is required unless the status is `backlog` must treat such a context the same way, because it fires first. `Repo.edit` refuses any other status, with a message saying to run `chitty move <ID> tasks`. `Repo.move` into such a context also sets `backlog`.

`chitty move <ID> tasks` already gives a ticket the target's next number and rewrites references, so it is the promotion, and its status stays `backlog` so the planning session can cold-read it. It refuses until the ticket has merged to `main`, because `_require_current_version` sends a person to the branch holding the newest copy: leave that alone, and say so in the note of the test.

## Acceptance Criteria

- [ ] Tests show `add` with `-s todo` creating a `backlog` ticket with no description needed, `edit -s todo` refused with that message, and `chitty move TASK-5 backlog` setting `backlog`
- [ ] A test on `main` shows `chitty move <ID> tasks` giving the next `TASK-` number, keeping `backlog`, and rewriting references in other tickets

## History

- 2026-11-05T14:47:51Z mellow-newt → backlog
