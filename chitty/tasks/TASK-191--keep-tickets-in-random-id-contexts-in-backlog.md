---
title: Keep tickets in random-ID contexts in `backlog`
status: doing
priority: high
depends_on:
  - TASK-190
parent: TASK-106
created: 2026-11-05
---

## Description

Second of three parts, after `TASK-190`. A ticket in a context with `random_ids` waits to be assessed, so it is always `backlog`, and leaves only by being moved. `Repo.add` sets `fields["status"] = "backlog"` before its checks of `done` and the description, whatever `-s` says. The check in `src/chitty/cli.py` that a description is required unless the status is `backlog` runs before `resolve_add_target`, so move it after that call and test the resolved context, not `-c`. `Repo.edit` refuses any other status, with a message saying to run `chitty move <ID> tasks`. `Repo.move` into such a context also sets `backlog`, recording it with `with_history`, because `with_field` writes no History entry. Set it on the moved ticket before the loop over other tickets: that loop reassigns `task`, so today `moved` is built from the last other ticket, and `Repo.move` needs a distinct variable there.

`chitty move <ID> tasks` already gives a ticket the target's next number and rewrites references, so it is the promotion, and its status stays `backlog` so the planning session can cold-read it. It refuses until the ticket has merged to `main`, because `_require_current_version` sends a person to the branch holding the newest copy: leave that alone, and say so in the note of the test.

## Acceptance Criteria

- [ ] Tests show `add` with `-s todo` creating a `backlog` ticket with no description needed, `edit -s todo` refused with that message, and `chitty move TASK-5 backlog` setting `backlog`
- [ ] A test in a Git repository, with the ticket committed on `main`, shows `chitty move <ID> tasks` giving the next `TASK-` number, keeping `backlog`, and rewriting references in other tickets, and the returned change showing the moved ticket's own title

## Notes

Cold read of the split by a fresh Sonnet subagent, 2026-11-05. Serious, both fixed: the description check runs before the context is known; and `Repo.move` reassigns `task` in a loop, an existing bug that would have lost the status and reports another ticket's content. Also fixed: recording History, the order in `Repo.add`, and the test needing a Git repository.

## History

- 2026-11-05T14:47:51Z mellow-newt → backlog
- 2026-11-05T14:50:40Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T14:50:41Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T14:50:42Z mellow-newt backlog → todo
- 2026-11-06T18:37:47Z mellow-gannet todo → doing
