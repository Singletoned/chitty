---
title: Give tickets raised on branches their own `BACKLOG` IDs
status: backlog
priority: high
parent: TASK-106
created: 2026-11-05
---

## Description

The human decided on 2026-11-05 that tickets raised by workers and reviewers should go to backlog with a separate, non-sequential ID, and be assessed in the planning session, which turns them into normally numbered tickets later. Then only `main` hands out sequential numbers, so branches cannot collide, however `TASK-177` counts them. This supersedes `TASK-61`, which reached the same place through the inbox.

Add a `backlog` context with prefix `BACKLOG`, whose IDs are random numbers rather than the next in sequence, such as `BACKLOG-48213907`. `TaskId` holds an integer, and a number needs no change to it, its ordering, filenames or `ID_RE`. Add a context setting named for its effect, `random_ids = true`, and in `Repo.next_number` pick a random 8-digit number from `secrets`, as a module-level constant, retrying if a known ticket uses it. Add the context to `INITIAL_CONFIG`, and have `chitty init` add it to existing repositories, or say in a note why it cannot.

`chitty add` run in a linked worktree with no `-c` uses this context; use `git.is_linked_worktree`. An explicit `-c` still wins, as `-c human` needs to. A ticket in such a context is always `backlog`: `add` forces that status, whatever `-s` says, and `edit` refuses any other, with a message saying to run `chitty move <ID> tasks`. That existing command gives the ticket the target's next number and rewrites references, so it is the promotion, run on `main` once the ticket has merged there. The status stays `backlog` afterwards, so the planning session can cold-read it.

`chitty next` already skips `backlog`. In `src/chitty/roles/work.md`, `review.md` and `src/chitty/guide.md`, say that unrelated work found on a ticket's branch goes in with plain `chitty add`, which files it as `BACKLOG` for the planning session.

Out of scope: IDs made of words, as in `BACKLOG-ember-dolphin-1`, because `TaskId.number` is an integer used throughout; and any change to `TASK-` numbering.

## Acceptance Criteria

- [ ] A test with a linked worktree shows plain `chitty add` creating a `BACKLOG-<8 digits>` ticket in `backlog`, whatever `-s` says, and `-c human` still numbering normally, and fails on a repeated random number by retrying
- [ ] A test shows `edit -s todo` refused on such a ticket, and `chitty move <ID> tasks` on `main` giving it the next `TASK-` number, keeping `backlog`, with references rewritten
- [ ] A test shows `chitty init` adding the context to an existing repository, `chitty check` passing with these tickets present, and `chitty next` never selecting one
- [ ] `chitty guide work` and `chitty guide review` say this, `PLAN.md` records the decision, and `__version__` is bumped above `main`'s

## History

- 2026-11-05T14:43:41Z mellow-newt → backlog
