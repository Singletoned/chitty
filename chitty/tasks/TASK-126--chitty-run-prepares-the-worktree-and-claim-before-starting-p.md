---
title: "`chitty run` prepares the worktree and claim before starting Pi"
status: todo
priority: high
depends_on:
  - TASK-124
parent: TASK-106
created: 2026-11-03
---

## Description

Make `chitty run` do the mechanical setup before starting Pi, so the agent starts in the right place with nothing to get wrong. These steps are currently prompt instructions, and they have failed: the `TASK-107` worker committed its claim on `main`, then ran `git reset --hard` in the main checkout (`TASK-121`). A script does them more reliably and for no tokens, and the prompts get shorter.

Before starting Pi, for the ticket `chitty next` chose:

1. Run the equivalent of `chitty inbox --pull` from the main checkout, if the repository has a `project`.
2. Find the ticket's worktree. If the ticket already has a branch, use its worktree, adding one at `.worktrees/<branch>` if none exists. If it has no branch, create branch `<id in lower case>` (for example `task-124`) from `main`, at `.worktrees/<branch>`. In mode `review`, a ticket with no branch is a loud error, as there is nothing to review.
3. Run the new `setup` command from `chitty.toml` in the worktree, every time, because dependencies may have changed since the last session. It is parsed without a shell, like `autoformat`. If it is unset, or fails, stop with a loud error and do not start Pi. It has no default, since a wrong guess would look like a working environment. Set `setup = "make install"` in this repository.
4. In mode `work`, if the ticket is `todo`, set it to `doing` in the worktree, so the claim is committed on the branch.
5. Start `pi --chitty-<mode> <ID>` with the worktree as its working directory, passing through any arguments given after `--`, as in `chitty run -- --model sonnet`. Pilot tickets need this to choose a model while keeping the automation; it replaces the `TASK-124` advice to call `pi` directly.

Actor: the claim and the Pi session must be one actor, different from every other run. Generate an ID for each `chitty run` and set `CHITTY_PI_SESSION_ID`, which the extension already leaves alone if set and subagents inherit. The claim then records the same actor as the session's work.

The extension then stops telling agents to do any of this. `pi --chitty-work` and `pi --chitty-review` refuse to start, with a message pointing at `chitty run`, unless the working directory is a linked Git worktree. That also guards the main checkout for Pi (`TASK-121`).

Out of scope: merging, gates and removing worktrees (`TASK-120`); non-Pi harnesses; `src/chitty/guide.md`, which still describes the manual steps for other agents.

## History

- 2026-11-03T16:30:14Z lively-panda → todo
